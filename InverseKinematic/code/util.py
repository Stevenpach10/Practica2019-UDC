import numpy as np
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta
from skimage.transform import rescale, resize, downscale_local_mean

def rescaleImage(strokes,init_size,end_size,xFactor, yFactor):
    new_stroke = []
    for stroke in strokes:
        x = end_size/(init_size/stroke[0])
        y = end_size/(init_size/stroke[1])
        new_stroke.append([x,y,stroke[2]])
    new_stroke = np.asarray(new_stroke)
    
    xMin = np.min(new_stroke[:,0])
    xMax = np.max(new_stroke[:,0])

    yMin = np.min(new_stroke[:,1])
    yMax = np.max(new_stroke[:,1])
    
    
    multiX = end_size/(xMax-xMin)
    multiY = end_size/(yMax-yMin)
    
    new_stroke[:,0] = new_stroke[:,0] * np.floor(multiX)
    new_stroke[:,1] = new_stroke[:,1] * np.floor(multiY)
    new_stroke = moveImage(new_stroke,xFactor,yFactor)
    return new_stroke

def moveImage(stroke_rescale, xFactor, yFactor):
    xMin = np.min(stroke_rescale[:,0])
    yMin = np.min(stroke_rescale[:,1])

    stroke_rescale[:,0] = (stroke_rescale[:,0] - (xMin * xFactor))
    stroke_rescale[:,1] = stroke_rescale[:,1] - (yMin * yFactor)
    return stroke_rescale

def diff_time(t_a, t_b):
    t_diff = relativedelta(t_b, t_a)  # later/end time comes first!
    return '{h}h {m}m {s}s'.format(h=t_diff.hours, m=t_diff.minutes, s=t_diff.seconds)

def rescaleImagePNG(image):
    image_rescaled = rescale(image, 0.093, anti_aliasing=False)
    return image_rescaled
    
def plotAllData(output,save=False,name="Image"):
  plt.plot(np.arange(0,len(output),1),output[:,0],'go-',label='Axis X',c='r')
  plt.legend()
  plt.xlabel('Time')
  plt.ylabel('Output of axis X')
  if save:
    plt.savefig(name + "_Axis_X")
  plt.show()

  plt.plot(np.arange(0,len(output),1),output[:,1],'go-',label='Axis Y',c='b')
  plt.legend()
  plt.xlabel('Time')
  plt.ylabel('Output of axis Y')
  if save:
    plt.savefig(name + "_Axis_Y")
  plt.show()

  plt.plot(np.arange(0,len(output),1),output[:,2],'go-',label='Axis Z',c='c')
  plt.legend()
  plt.xlabel('Time')
  plt.ylabel('Output of axis Z')
  if save:
    plt.savefig(name + "_Axis_Z")
  plt.show()