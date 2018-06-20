import plonny
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from layergrid import LayerGrid
from plonny import GraphParam
sns.set()

def defineFigure():
    """Setup plot"""
    fig = plt.figure(figsize=(10,10))
    axes = fig.add_subplot(111)
    # plt.axis('off')
    plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
    plt.ylim(0, 1)
    plt.xlim(0, 1)
    return axes

class Graph(object):
    """Controls a structured grid for a graph."""

    def __init__(self, graph=None):
        self.lgrid = LayerGrid()
        if(isinstance(graph, Graph)):
            self.lgrid = graph.lgrid
        if(isinstance(graph, LayerGrid)):
            self.lgrid = graph

    def graphshow(self, title="Neural Network"):
        ax = defineFigure()

        # calculate dimensions for the rectilinear grid
        colWidths = [0] * len(self.lgrid.cols())
        rowHeights = [0] * len(self.lgrid.rows())

        for colIdx, column in enumerate(self.lgrid.cols()):
            colWidths[colIdx] = max([layer.shape[0] for layer in column])
        for rowIdx, row in enumerate(self.lgrid.rows()):
            rowHeights[rowIdx] = max([layer.shape[1] for layer in row])

        # calculate layer screen dimensions based on grid
        for row in self.lgrid.rows():
            for layer in row:
                layer.setDimensions(colWidths, rowHeights)

        # Create screen space version of rectilinear grid
        ss_col_widths = [0] * len(colWidths)
        ss_row_heights = [0] * len(rowHeights)
        for rowIdx in range(len(rowHeights)):
            for colIdx in range(len(colWidths)):
                max_height = plonny.scale2Screen(rowHeights[rowIdx], rowHeights, 0, .25) #use labelheight spacing
                max_full_width = colWidths[colIdx] / rowHeights[rowIdx] * max_height
                max_full_width = np.sum(colWidths) / colWidths[colIdx] * max_full_width + GraphParam.spacing * (len(colWidths) - 1)

                ss_col_widths[colIdx] = plonny.scale2Screen(colWidths[colIdx], colWidths, GraphParam.spacing, min(1, max_full_width))
                ss_row_heights[rowIdx] = rowHeights[rowIdx] / colWidths[colIdx] * ss_col_widths[colIdx]
        print("ss_col_widths", ss_col_widths)
        print("ss_row_heights", ss_row_heights)

        # set layer plotting properties
        # xy = {'x':.5 * (1 - np.sum([layer.width for layer in self.lgrid.grid[0]])),'y':0}
        xy = {'x':.5 * (1 - np.sum([layer.width for layer in self.lgrid.grid[0]])),'y':0}
        for colIdx, layer in enumerate(self.lgrid.grid[0]):
            # layer.setDimensions(self.lgrid.grid[0], [self.lgrid.grid[0][0]])
            xy['y'] = .5 - .5 * layer.height + GraphParam.txt_margin
            layer.xy        = dict(xy)

            # Update x position
            # xy['x'] += layer.width + GraphParam.spacing
            xy['x'] += ss_col_widths[colIdx] + GraphParam.spacing

        # set titles locations and plot
        maxheight = np.max([layer.height for layer in self.lgrid.grid[0]])
        GraphParam.txt_height = 0.5 - .5 * maxheight - 2*GraphParam.txt_margin
        GraphParam.titleheight = 0.5 + .5 * maxheight + 4*GraphParam.txt_margin
        plt.text(0.5, GraphParam.titleheight, title, horizontalalignment='center')

        # Iterate layers, plotting their output shapes
        self.lgrid.grid[0][0].show(ax)
        for current, layer in enumerate(self.lgrid.grid[0][1:], 1):
            layer.show(ax, [self.lgrid.grid[0][current-1]])

        plt.show()

if __name__ == "__main__":
    l0 = plonny.Input((32, 32, 1))
    l1 = plonny.Conv2D(l0, (32, 32, 1), (3,3))
    l2 = plonny.Conv2D(l1, (32, 32, 1), (3,3))
    l3 = plonny.Conv2D(l2, (32, 32, 1), (3,3))
    l4 = plonny.Conv2D(l3, (32, 32, 1), (3,3))
    l5 = plonny.Conv2D(l4, (32, 32, 1), (3,3))

    lg = LayerGrid()
    lg.set(0, 0, l0)
    lg.set(0, 1, l1)
    # lg.set(1, 2, l1)
    # lg.set(0, 2, l2)
    # lg.set(0, 3, l3)
    # lg.set(0, 4, l4)
    # lg.set(0, 5, l5)
    print(lg.grid)

    Graph(lg).graphshow()