from main import DepthCamera
dc = DepthCamera()
ret, depth_frame, color_frame = dc.get_frame() #get the frame objects
