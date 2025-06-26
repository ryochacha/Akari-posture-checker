import numpy as np
import cv2

# Dictionary that maps from joint names to keypoint indices.
KEYPOINT_DICT = {
    'nose': 0,
    'left_eye_inner': 1,
    'left_eye': 2,
    'left_eye_outer': 3,
    'right_eye_inner': 4,
    'right_eye': 5,
    'right_eye_outer': 6,
    'left_ear': 7,
    'right_ear': 8,
    'mouth_left': 9,
    'mouth_right': 10,
    'left_shoulder': 11,
    'right_shoulder': 12,
    'left_elbow': 13,
    'right_elbow': 14,
    'left_wrist': 15,
    'right_wrist': 16,
    'left_pinky': 17,
    'right_pinky': 18,
    'left_index': 19,
    'right_index': 20,
    'left_thumb': 21,
    'right_thumb': 22,
    'left_hip': 23,
    'right_hip': 24,
    'left_knee': 25,
    'right_knee': 26,
    'left_ankle': 27,
    'right_ankle': 28,
    'left_heel': 29,
    'right_heel': 30,
    'left_foot_index': 31,
    'right_foot_index': 32
}

#LINES_BODY are used to draw the skeleton
LINES_BODY = [[28,30],[30,32],[27,29],[29,31],[28,26],[26,24],[24,23],[23,25],[25,27],[24,12],[12,11],[11,23],
            [12,14],[14,16],[16,20],[16,18],[16,22],[18,20],
            [11,13],[13,15],[15,19],[15,17],[15,21],[17,19],
            [6,5],[5,4],[4,0],[0,1],[1,2],[2,3],[9,10]]

class Body:
    """
    Body class:
    Attributes:
    - landmarks: 3D landmarks in the image coordinate system (in pixel)
    - landmarks_world: 3D landmarks in the world coordinate system (in meter)
    - landmarks_norm: 2D landmarks in the image coordinate system (in pixel)
                    normalized ([0:1]) in the square crop during landmarks inference
    - score: score of the body detection
    - lm_score: score of the landmarks model detection
    - handedness: "left" or "right" handedness of the hand
    """
    def __init__(self, pd_kps=None, pd_score=0, rect_x_center=0, rect_y_center=0, rect_w=0, rect_h=0, rotation=0, rect_points=None):
        self.pd_kps = pd_kps
        self.pd_score = pd_score
        self.rect_x_center = rect_x_center
        self.rect_y_center = rect_y_center
        self.rect_w = rect_w
        self.rect_h = rect_h
        self.rotation = rotation
        self.rect_points=rect_points
        self.landmarks = np.zeros((39,3))
        self.landmarks_world = np.zeros((39,3))
        self.landmarks_norm = np.zeros((39,3))
        self.visibility = np.zeros(39)
        self.presence = np.zeros(39)
        self.lm_score = 0
        self.xyz = np.zeros(3)
        self.xyz_ref = None # "mid_hips" or "mid_shoulders"
        self.xyz_ref_coords_pixel = np.zeros(2)


    def print(self):
        print("pd_score:", self.pd_score)
        print("lm_score:", self.lm_score)
        for i in range(self.landmarks.shape[0]):
            print(i, self.landmarks[i], self.landmarks_world[i], self.visibility[i], self.presence[i])

def find_isp_scale_params(size, is_height=True):
    """
    Find closest valid size close to 'size' and the corresponding parameters to setIspScale()
    This function is useful to work around a bug in depthai where ImageManip is scrambling images that have an invalid size
    is_height : boolean that indicates if the value 'size' corresponds to the desired height or width
    """
    # We want to find the smallest integers p and q such that:
    # w/h = 1920/1080 = 16/9
    # (size * p / q) % 16 == 0
    # and abs(size * p / q - size) is minimum
    #
    # Let's rewrite this as:
    # size * p = 16 * k * q
    # p = 16*k*q/size
    #
    # We are looking for p, q integers that are not too big
    q = 1
    while True:
        p_float = 16*q/size
        if abs(p_float - round(p_float)) < 0.02:
            p = round(p_float)
            if p!=0:
                break
        q += 1
    k=1
    while True:
        p_float = 16*k*q/size
        if p_float > 50: break # Let's consider that p and q are not too big
        if abs(p_float - round(p_float)) < 0.01:
            p = round(p_float)
            if p!=0:
                new_size = size * p / q
                if new_size % 16 == 0:
                    if is_height:
                        width = new_size * 16 / 9
                        if width % 2 == 0: break
                    else:
                        height = new_size * 9 / 16
                        if height % 2 == 0: break
        k += 1
    return int(new_size), (p,q)


def generate_blazepose_anchors():
    """
    From mediapipe/modules/pose_detection/pose_detection_cpu.pbtxt
    Returns:
        anchors: a numpy array of shape (2254, 4)
    """
    strides = [8, 16]
    assert len(strides) == 2, "Wrong number of strides"
    img_size = 224
    anchors = []
    for i in range(len(strides)):
        stride = strides[i]
        grid_rows = img_size // stride
        grid_cols = img_size // stride
        
        for r in range(grid_rows):
            for c in range(grid_cols):
                x_center = (c + 0.5) / grid_cols
                y_center = (r + 0.5) / grid_rows
                
                if stride == 8:
                    num_anchors = 2
                    anchor_h = [0.265625, 0.53125]
                    anchor_w = [0.203125, 0.40625]
                else: # stride == 16
                    num_anchors = 6
                    anchor_h = [0.734375, 0.96875, 1.34375, 1.75, 2.34375, 3.46875]
                    anchor_w = [0.5, 0.65625, 0.84375, 1.0625, 1.34375, 1.71875]

                for j in range(num_anchors):
                    anchors.append([x_center, y_center, anchor_w[j], anchor_h[j]])
    
    return np.array(anchors)


def decode_bboxes(score_thresh, scores, bboxes, anchors, best_only=False):
    """
    scores: shape: (1, 2254, 1)
    bboxes: shape: (1, 2254, 12)
    anchors: shape: (2254, 4)
    """
    bodies = []
    
    scores = scores[0,:,0]
    # TODO: what are the 0x2254x1 scores ?
    # There are 2254 anchors, which multiplied by 1 score makes 2254 scores
    # What are these scores ? The doc says "The detection model produces a score for each predicted pose."
    # Yes, but there are 2254 predicted poses. So these scores are the scores of the 2254 predicted poses.
    
    # Select the bboxes for which score is over the threshold
    mask = scores > score_thresh
    scores = scores[mask]
    bboxes = bboxes[0,mask,:]
    anchors = anchors[mask,:]
    if scores.size == 0:
        return bodies

    # Decode bboxes
    # bboxes are in this format:
    # 0: rect_x_center_a
    # 1: rect_y_center_a
    # 2: rect_w_a
    # 3: rect_h_a
    # 4: kp_0_x_a
    # 5: kp_0_y_a
    # 6: kp_1_x_a
    # 7: kp_1_y_a
    # ...
    # Here, we are only interested in the first 4 components
    
    # The bboxes are on a 224x224 images
    # The anchors are normalized
    img_size = 224 
    x_center = bboxes[:,0] / img_size + anchors[:,0]
    y_center = bboxes[:,1] / img_size + anchors[:,1]
    w = bboxes[:,2] / img_size * anchors[:,2]
    h = bboxes[:,3] / img_size * anchors[:,3]
    
    bboxes_scaled = np.concatenate((
        x_center.reshape(-1,1),
        y_center.reshape(-1,1),
        w.reshape(-1,1),
        h.reshape(-1,1)
    ), axis=1)
    
    # Non-maximum suppression to remove overlapping bounding boxes
    #nms_indices = tf.image.non_max_suppression(bboxes_scaled, scores, max_output_size, iou_threshold)
    # nms_indices is a list of indices of the best detections
    # for i in nms_indices:
    #     body = Body(pd_score=scores[i])
    #     body.rect_x_center, body.rect_y_center, body.rect_w, body.rect_h = bboxes_scaled[i]
    #     body.pd_kps = (bboxes[i,4:].reshape(-1,2) + anchors[i,:2]*img_size).astype(np.int32)
    #     bodies.append(body)

    # For now, we are not using NMS, but we are only considering the best detection.
    # It is not optimal, but it is better than nothing
    
    i = np.argmax(scores)
    body = Body(pd_score=scores[i])
    body.rect_x_center_a, body.rect_y_center_a, body.rect_w_a, body.rect_h_a = bboxes_scaled[i]
    # The keypoints are on a 224x224 image
    body.pd_kps = (bboxes[i,4:].reshape(-1,2) / img_size + anchors[i,:2]).reshape(-1,2)

    bodies.append(body)
    
    return bodies

def detections_to_rect(body):
    # Converts a rotated bounding box to a non-rotated bounding box.
    # The output bounding box is slightly bigger than the input one
    
    # body.pd_kps are the 2 keypoints of the body, normalized to [0,1]
    # The first keypoint is the center of the hips
    # The second keypoint is the center of the shoulders
    # TODO: the second keypoint is not the center of the shoulders, it is above the head
    # We are using the distance between the 2 keypoints as the height of the person
    # and the width is calculated from the height
    # The center of the bouding box is the center of the hips

    # rect_width = rect_height = hypot(
    #     body.pd_kps[1,0] - body.pd_kps[0,0],
    #     body.pd_kps[1,1] - body.pd_kps[0,1]) * 2.0 * 1.25 #rect_scale
    
    # rect_x_center = body.pd_kps[0,0]
    # rect_y_center = body.pd_kps[0,1]
    # For the rotation, we are using the angle of the line between the 2 keypoints
    # rotation = 0.5 * np.pi - np.arctan2(
    #    body.pd_kps[1,1] - body.pd_kps[0,1],
    #     body.pd_kps[1,0] - body.pd_kps[0,0])
    
    # body.rect_w = body.rect_h = rect_width
    # body.rect_x_center = rect_x_center
    # body.rect_y_center = rect_y_center
    # body.rotation = rotation

    # For now, we are not using the keypoints to calculate the bounding box
    # but the bounding box from the pose detection model
    body.rect_x_center = body.rect_x_center_a 
    body.rect_y_center = body.rect_y_center_a
    body.rect_w = body.rect_h = max(body.rect_w_a, body.rect_h_a)
    body.rotation = 0


def rect_transformation(body, w, h, scale, rotation_in_rad=None):
    """
    w,h: frame width and height
    scale: float used to scale the rotated rectangle
    """
    if rotation_in_rad is None:
        body.rotation = body.rotation + np.pi/2
    else:
        body.rotation = rotation_in_rad
        
    body.rect_w_a = int(body.rect_w * w * scale)
    body.rect_h_a = int(body.rect_h * h * scale)
    
    body.rect_x_center_a = body.rect_x_center * w
    body.rect_y_center_a = body.rect_y_center * h

    sin = np.sin(body.rotation)
    cos = np.cos(body.rotation)

    # The 4 points of the rotated rectangle
    points = []
    points.append(
        (
            int(body.rect_x_center_a + body.rect_w_a/2 * cos - body.rect_h_a/2 * sin),
            int(body.rect_y_center_a - body.rect_w_a/2 * sin - body.rect_h_a/2 * cos)
        )
    )
    points.append(
        (
            int(body.rect_x_center_a - body.rect_w_a/2 * cos - body.rect_h_a/2 * sin),
            int(body.rect_y_center_a + body.rect_w_a/2 * sin - body.rect_h_a/2 * cos)
        )
    )
    points.append(
        (
            int(body.rect_x_center_a - body.rect_w_a/2 * cos + body.rect_h_a/2 * sin),
            int(body.rect_y_center_a + body.rect_w_a/2 * sin + body.rect_h_a/2 * cos)
        )
    )
    points.append(
        (
            int(body.rect_x_center_a + body.rect_w_a/2 * cos + body.rect_h_a/2 * sin),
            int(body.rect_y_center_a - body.rect_w_a/2 * sin + body.rect_h_a/2 * cos)
        )
    )
    body.rect_points = points


def warp_rect_img(rect_points, frame, w, h):
        
    src_points = np.array(rect_points, dtype=np.float32)
    dst_points = np.array([[0,h],[w,h],[w,0]], dtype=np.float32)
    mat = cv2.getAffineTransform(src_points[1:], dst_points)
    result_img = cv2.warpAffine(frame, mat, (w, h))
    return result_img

class LandmarksSmoothingFilter:
    def __init__(self, frequency, min_cutoff, beta, derivate_cutoff, 
                disable_value_scaling=False):
        self.sequence_length = 39
        self.x_history = [None] * self.sequence_length
        self.y_history = [None] * self.sequence_length
        self.z_history = [None] * self.sequence_length
        for i in range(self.sequence_length):
            self.x_history[i] = self.OneEuroFilter(frequency, min_cutoff, beta, derivate_cutoff)
            self.y_history[i] = self.OneEuroFilter(frequency, min_cutoff, beta, derivate_cutoff)
            self.z_history[i] = self.OneEuroFilter(frequency, min_cutoff, beta, derivate_cutoff)
        self.disable_value_scaling = disable_value_scaling
    
    def apply(self, landmarks, timestamp, object_scale = 1.0):
        # landmarks is a numpy array of shape (self.sequence_length, 3)
        # timestamp is a float
        # object_scale is a float
        for i in range(self.sequence_length):
            if self.disable_value_scaling:
                landmarks[i,0] = self.x_history[i].apply(landmarks[i,0], timestamp)
                landmarks[i,1] = self.y_history[i].apply(landmarks[i,1], timestamp)
                landmarks[i,2] = self.z_history[i].apply(landmarks[i,2], timestamp)
            else:
                landmarks[i,0] = self.x_history[i].apply(landmarks[i,0], timestamp, object_scale)
                landmarks[i,1] = self.y_history[i].apply(landmarks[i,1], timestamp, object_scale)
                landmarks[i,2] = self.z_history[i].apply(landmarks[i,2], timestamp, object_scale)
        return landmarks

    def reset(self):
        for i in range(self.sequence_length):
            self.x_history[i].reset()
            self.y_history[i].reset()
            self.z_history[i].reset()

    class OneEuroFilter:
        def __init__(self, frequency, min_cutoff, beta, derivate_cutoff):
            self.frequency = frequency
            self.min_cutoff = min_cutoff
            self.beta = beta
            self.derivate_cutoff = derivate_cutoff
            self.reset()
        
        def reset(self):
            self.x_previous = None
            self.dx_previous = None
            self.last_timestamp = None

        def apply(self, x, timestamp, object_scale=1.0):
            if self.last_timestamp and timestamp and self.last_timestamp > timestamp:
                self.reset()
            
            if self.x_previous is None:
                self.x_previous = x
                self.last_timestamp = timestamp
                return x

            if self.last_timestamp:
                self.frequency = 1.0 / (timestamp - self.last_timestamp)
            self.last_timestamp = timestamp

            # Filter dx
            if self.dx_previous is None:
                self.dx_previous = 0
            else:
                self.dx_previous = (x - self.x_previous) * self.frequency
            
            alpha_d = self.get_alpha(self.derivate_cutoff)
            dx = (1.0 - alpha_d) * self.dx_previous + alpha_d * self.dx_previous
            self.dx_previous = dx

            # Filter x
            cutoff = self.min_cutoff + self.beta * abs(dx * object_scale)
            alpha = self.get_alpha(cutoff)
            x_filtered = (1.0 - alpha) * self.x_previous + alpha * x
            self.x_previous = x_filtered

            return x_filtered


        def get_alpha(self, cutoff):
            return 1.0 / (1.0 + (self.frequency / (2.0 * np.pi * cutoff)))

class LowPassFilter:
  def __init__(self, alpha):
    self.alpha = alpha
    self.initialized = False

  def apply(self, x):
    if self.initialized:
      self.x_filtered = self.alpha * x + (1.0 - self.alpha) * self.x_filtered
    else:
      self.x_filtered = x
      self.initialized = True
    return self.x_filtered

  def reset(self):
    self.initialized = False