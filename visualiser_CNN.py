import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.collections import PatchCollection
import numpy as np
import seaborn as sns
sns.set()

def show_basiclayer(self, axes, param, inputs=[]):
    """Default plot for Input and Layer"""
    # Annotate dimensions and layer
    plt.text(self.xy['x']+.5*self.width, self.xy['y']-param['txt_margin'], self.shape[0], rotation=0)
    plt.text(self.xy['x'], self.xy['y'] + .5*self.height, self.shape[1], rotation=90)
    if len(self.shape) > 2:
        plt.text(self.xy['x'], self.xy['y'] + self.height + param['txt_margin'], self.depth, rotation=45)
    plt.text(self.xy['x'], param['txtheight'], type(self).__name__, rotation=90)

    # Draw shape
    for z in reversed(range(self.depth)):
        # Color calculation
        d = (1 - z/self.depth) * 0.8 + 0.2
        color = tuple([.4* d, .5* d, 1* d])

        # draw output shape
        xyd = {key: self.xy[key] + param['depth_spacing'] * (z/self.depth) for key in self.xy.keys()}
        rect = patches.Rectangle(   tuple(xyd.values()),
                                    self.width,
                                    self.height,
                                    color=color,
                                    linewidth=1)#, edgecolor='r', facecolor='none'
        axes.add_patch(rect)

class Input(object):
    def __init__(self, shape):
        self.shape = shape
        self.graph = [self]

    show = show_basiclayer

class Layer(object):
    def __init__(self, layer):
        if(not isinstance(layer, Layer) and not isinstance(layer, Input)):
            raise AssertionError("A new layer was requested attached to neither a layer or an input.", str(layer))
        self.graph = layer.graph + [self]
        self.shape = None

        self.param = {
            'txtheight'       : .95,                #where to draw text. plot top=1
            'txt_margin'      : 0.05,               #offsets for shape annotators
            'spacing'         : 0.05,               #horizontal space between shapes
            'maxHeight'       : 0.65               #no higher than 2/3
        }
        #how far deep layers go to back
        self.param['depth_spacing'] = .5*self.param['spacing']

    show = show_basiclayer

    def _width2w(self, width, graph=None):
        """Convert width in shape space to coordinate space width"""
        graph = self.graph if graph is None else graph

        spacings = self.param['spacing'] * (len(graph)-1)
        totalwidths = np.sum([layer.shape[0] for layer in graph])
        return width / totalwidths * (1 - spacings)

    def calcMaxShape(self, graph=None):
        """Returns maximum dimensions of all layer outputs"""
        graph = self.graph if graph is None else graph

        maxShape = [0,0,0]
        for layer in graph:
            for dim in range(len(layer.shape)):
                if layer.shape[dim] > maxShape[dim]:
                    maxShape[dim] = layer.shape[dim]
        return {'w':maxShape[0], 'h':maxShape[1], 'd':maxShape[2]}

    def output_shape(self, graph=None):
        maxShape = self.maxShape(graph)

        width = self._width2w(shp[0])
        height = shp[1] / maxShape['h'] * self.param['maxHeight']
        depth = shp[2] if len(shp) > 2 else 1
        return (width, height, depth)

    def graphshow(self, title=None):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plt.axis('off')
        plt.ylim(0, 1)
        if(title is not None):
            plt.text(0.5, 1.05, title, horizontalalignment='center')

        # get max shapes
        maxShape = self.calcMaxShape()

        # set layer plotting properties
        xy = {'x':0,'y':0}
        for layer in self.graph:
            shp = layer.shape
            layer.width     = self._width2w(shp[0])
            layer.height    = shp[1] / maxShape['h'] * self.param['maxHeight']
            layer.depth     = shp[2] if len(shp) > 2 else 1
            layer.maxShape  = maxShape

            xy['y'] = .5 * self.param['maxHeight'] - .5 * layer.height + self.param['txt_margin']
            layer.xy        = dict(xy)

            # Update x position
            xy['x'] += layer.width + self.param['spacing']

        # Iterate layers, plotting their output shapes
        for ctr, layer in enumerate(self.graph):
            if(ctr>0):
                layer.show(ax, self.param, [self.graph[ctr-1]])
            else:
                layer.show(ax, self.param)
            # layer.show(ax, self.param)

        plt.show()

class Conv2D(Layer):
    def __init__(self, layer, shape, kernel):
        Layer.__init__(self, layer);
        self.shape = shape
        self.kernel = kernel

    def show(self, axes, param, inputs=[]):
        """Default plot for Input and Layer"""
        # Annotate dimensions and layer
        plt.text(self.xy['x']+.5*self.width, self.xy['y']-param['txt_margin'], self.shape[0], rotation=0)
        plt.text(self.xy['x'], self.xy['y'] + .5*self.height, self.shape[1], rotation=90)
        if len(self.shape) > 2:
            plt.text(self.xy['x'], self.xy['y'] + self.height + param['txt_margin'], self.depth, rotation=45)
        plt.text(self.xy['x'], param['txtheight'], type(self).__name__, rotation=90)

        # Draw shape
        for z in reversed(range(self.depth)):
            # Color calculation
            d = (1 - z/self.depth) * 0.8 + 0.2
            color = tuple([.4* d, .5* d, 1* d])

            # draw output shape
            xyd = {key: self.xy[key] + param['depth_spacing'] * (z/self.depth) for key in self.xy.keys()}
            rect = patches.Rectangle(   tuple(xyd.values()),
                                        self.width,
                                        self.height,
                                        color=color,
                                        linewidth=1)#, edgecolor='r', facecolor='none'
            axes.add_patch(rect)

        # draw kernel connections
        input = inputs[0]
        kerncol = (0, 0, 0)
        self.kernel_rel = (self.kernel[0] * input.width / input.shape[0], self.kernel[1] * input.height / input.shape[1])
        kernel_pos = (input.xy['x'] + input.width - self.kernel_rel[0], input.xy['y'] + input.height - self.kernel_rel[1])
        rect = patches.Rectangle(   kernel_pos,
                                    self.kernel_rel[0],
                                    self.kernel_rel[1],
                                    color=kerncol,
                                    linewidth=1)#, edgecolor='r', facecolor='none'
        axes.add_patch(rect)

        # draw kernel connections
        down = list(kernel_pos)
        down[0] = down[0] + self.kernel_rel[0]
        up = list(down)
        up[1] += self.kernel_rel[1]
        dest = dict(self.xy)
        dest['y'] += self.height
        plt.plot([down[0], dest['x']], [down[1], dest['y']], linewidth=.5, alpha=0.9, color=kerncol)
        plt.plot([up[0], dest['x']], [up[1], dest['y']], linewidth=.5, alpha=0.9, color=kerncol)

class Pool(Layer):
    def __init__(self, layer, shape):
        Layer.__init__(self, layer);
        self.shape = shape

class Reshape(Layer):
    def __init__(self, layer, shape):
        Layer.__init__(self, layer);
        self.shape = shape

class FC(Layer):
    def __init__(self, layer, neurons):
        Layer.__init__(self, layer);
        self.shape = (1, neurons)

    def show(self, axes, param, inputs=[]):
        """Plot this layer"""
        # Annotate dimensions and layer
        plt.text(self.xy['x'], self.xy['y'] + .5*self.height, self.shape[1], rotation=90)
        plt.text(self.xy['x'], param['txtheight'], type(self).__name__, rotation=90)

        n_neurons = self.shape[1]
        for neuron in range(n_neurons):
            # draw neurons
            color = (.4, .5, 1)
            xyn = dict(self.xy)
            xyn['y'] += neuron * self.height / n_neurons
            circ = patches.Circle(      tuple(xyn.values()),
                                        radius = 0.1 * self.height / n_neurons,
                                        color=color,
                                        linewidth=1)
            axes.add_patch(circ)

            # draw connections
            color = (0, 0, 0)
            for layer in inputs:
                for vert in range(layer.shape[1]):
                    xy_dest = ( layer.xy['x'] + layer.width,
                                layer.xy['y'] + (vert/layer.shape[1]) * layer.height)
                    plt.plot([xyn['x'], xy_dest[0]], [xyn['y'], xy_dest[1]], linewidth=.1, alpha=0.1, color=color)
class CTC(Layer):
    def __init__(self, layer, shape):
        Layer.__init__(self, layer);
        self.shape = shape

if __name__ == "__main__":
    # Define model by calling layers
    image_0 = Input((32, 128, 1))

    conv2_1 = Conv2D(image_0, (32, 128, 16), (3,3))
    Pool_2  = Pool(conv2_1, (16, 64, 16))

    conv2_3 = Conv2D(Pool_2, (16, 64, 64), (3,3))
    Pool_4  = Pool(conv2_3, (8, 32, 64))

    conv2_5 = Conv2D(Pool_4, (8, 32, 64), (3,3))
    Pool_6  = Pool(conv2_5, (4, 16, 64))

    conv2_7 = Conv2D(Pool_6, (4, 16, 64), (3,3))
    conv2_8 = Conv2D(conv2_7, (4, 16, 16), (3,3))
    conv2_9 = Conv2D(conv2_8, (4, 16, 7), (3,3))

    resh_10 = Reshape(conv2_9, (8, 56))
    conv_11 = Conv2D(resh_10, (8, 28), (3,3))

    fccc_12 = FC(conv_11, 8)

    fccc_13 = FC(fccc_12, 50)

    fccc_13.graphshow("Neural Network")
