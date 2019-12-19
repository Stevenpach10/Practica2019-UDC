#****************************************************************************
#Image replication with the robotic device Poppy in a virtual simulator     *
#V-REP. Developed within the framework of the Professional Practice         *
#course-IC8842 of the bachelor's degree in Computer Engineering,            *
#Technological Institute of Costa Rica. With the support of the Integrated  *
#Engineering Group located on the Ferrol Campus of the University of Coruna *
#2019 Steven Andrey Pacheco Portuguez, Coruna, Espana                       *
#email stpacheco@ic-itcr.ac.cr                                              *
#****************************************************************************
import numpy as np
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta
from skimage.transform import rescale, resize, downscale_local_mean


def rescaledImage(strokes, pixel_size, end_size, xFactor, yFactor):
    """Rescale an image's strokes for drawing with Poppy. 

    Parameters
    -------------------
    strokes: List
        List with all points that correspond with the image to draw
    pixel_size: Integer
        Size in pixels of the input image. Example 48 in this case.
    end_size: Float
        Size target in meters.
    xFactor: Float
        How much have to  move the image in the axis X. Zero does not have to move
    yFactor: Float
        How much have to move the iamge in the axis Y. Zero does not have to move

    Returns
    ------------------
    list
        Strokes rescaled of the image to draw. 
    """
    new_stroke = []
    for stroke in strokes:
        x = end_size/(pixel_size/stroke[0])
        y = end_size/(pixel_size/stroke[1])
        new_stroke.append([x, y, stroke[2]])
    new_stroke = np.asarray(new_stroke)

    xMin = np.min(new_stroke[:, 0])
    xMax = np.max(new_stroke[:, 0])

    yMin = np.min(new_stroke[:, 1])
    yMax = np.max(new_stroke[:, 1])

    multiX = end_size/(xMax-xMin)
    multiY = end_size/(yMax-yMin)

    new_stroke[:, 0] = new_stroke[:, 0] * np.floor(multiX)
    new_stroke[:, 1] = new_stroke[:, 1] * np.floor(multiY)
    new_stroke = moveImage(new_stroke, xFactor, yFactor)
    return new_stroke


def moveImage(stroke_rescale, xFactor, yFactor):
    """Allow move the image in the axis X and Y  

    Parameters
    -------------------
    stroke_rescale: List
      Strokes rescaled of the image.
    xFactor: Float
        How much have to  move the image in the axis X. Zero does not have to move
    yFactor: Float
        How much have to move the iamge in the axis Y. Zero does not have to move

    Returns
    ------------------
    list
        Strokes rescaled of the image to draw. 
    """
    xMin = np.min(stroke_rescale[:, 0])
    yMin = np.min(stroke_rescale[:, 1])

    stroke_rescale[:, 0] = (stroke_rescale[:, 0] - (xMin * xFactor))
    stroke_rescale[:, 1] = stroke_rescale[:, 1] - (yMin * yFactor)
    return stroke_rescale


def diff_time(start_time, end_time):
  """Get the difference time between two values.
    Parameters
    -------------------
    start_time: Datetime
      Initial datetime 
    end_time: Datetime
      Final datetime
    Returns
    ------------------
    list
      String with the format time result 
  """
  t_diff = relativedelta(end_time, start_time)
  return '{h}h {m}m {s}s'.format(h=t_diff.hours, m=t_diff.minutes, s=t_diff.seconds)


def plotAllData(output, save=False, name="Image"):
    """Plot the movements in each axis

    Parameters
    -------------------
    output: List
      List of effectors in each move. with the shape (N, 3)
    save: Boolean, optional
        If save is True, the figure will be saved at the root directory project. By default is False
    name: String
        Name of the file. By default is Image

    """
    plt.plot(np.arange(0, len(output), 1),
             output[:, 0], 'go-', label='Axis X', c='r')
    plt.legend()
    plt.xlabel('Time')
    plt.ylabel('Output of axis X')
    if save:
        plt.savefig(name + "_Axis_X")
    plt.show()

    plt.plot(np.arange(0, len(output), 1),
             output[:, 1], 'go-', label='Axis Y', c='b')
    plt.legend()
    plt.xlabel('Time')
    plt.ylabel('Output of axis Y')
    if save:
        plt.savefig(name + "_Axis_Y")
    plt.show()

    plt.plot(np.arange(0, len(output), 1),
             output[:, 2], 'go-', label='Axis Z', c='c')
    plt.legend()
    plt.xlabel('Time')
    plt.ylabel('Output of axis Z')
    if save:
        plt.savefig(name + "_Axis_Z")
    plt.show()
def drawAbsolutePosition(strokes_abs,limits):
    """Plot all points in a canvas for visualization. 

    Parameters
    -------------------
    strokes_abs: List
        List with all strokes of an image in absolute position.
    limits: List
        List with two float value for set the limit of the canvas. (X, Y)
    """
    x = strokes_abs[:,0]
    y = strokes_abs[:,1]
    plt.scatter(x, y)
    plt.xlim(limits[0], limits[1])
    plt.ylim(limits[2], limits[3])
    plt.show()