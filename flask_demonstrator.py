import json
from flask import Flask, render_template, Response, request, redirect
from dronecamera import DroneCamera

app = Flask(__name__)
global_camera = DroneCamera().__enter__()

@app.route('/')
def index():
    """Returns index page template."""
    return render_template('index.html')

def gen(camera):
    """Generator function that continually requests a frame from the frames 
    buffer, and writes it to the HTML page.

    :type camera: DroneCamera
    :param camera: The DroneCamera object
    """
        for frame in camera.frames():
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/stream.mjpg')        
def video_feed():
    """Retrieves frames from the generator function whenever the video stream
    object on the HTML page is requested.
    """
    parts = gen(global_camera)
    return Response(parts,\
        mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/zoom', methods = ['GET', 'PUT'])
def zoom():
    """Writes and reads to the zoom level of the camera."""
    if request.method == 'PUT':
        # Write to zoom level:
        zoom = int(request.data)
        global_camera.set_zoom(zoom)
        return Response()
    else:
        # Reads current zoom level:
        zoom = str(global_camera.get_zoom())
        return Response(zoom, mimetype='application/json')

@app.route('/capture')
def capture():
    """Redirects user to a link where upon their browser downloads a snapshot 
    of the camera."""
    (x, y) = global_camera.get_coordinates()
    # Label snapshot image with the x- and y-coordinates:
    path = "/capture/X{}Y{}.jpeg".format(x,y)
    return redirect(path)

@app.route('/capture/<filename>')
def capture_with_filename(**kwargs):
    """Downloads a snapshot of the camera."""
    return Response(global_camera.frame(), mimetype='image/jpeg')

def main():
    """Runs this flask application on local network."""
    app.run(host='0.0.0.0')

if __name__ == "__main__":
    main()