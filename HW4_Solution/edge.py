import numpy as np

def conv(image, kernel):
    """ An implementation of convolution filter.

    This function uses element-wise multiplication and np.sum()
    to efficiently compute weighted sum of neighborhood at each
    pixel.

    Args -
        image: numpy array of shape (Hi, Wi).
        kernel: numpy array of shape (Hk, Wk).

    Returns -
        out: numpy array of shape (Hi, Wi).
    """
    Hi, Wi = image.shape
    Hk, Wk = kernel.shape
    out = np.zeros((Hi, Wi))

    # For this assignment, we will use edge values to pad the images.
    # Zero padding will make derivatives at the image boundary very big,
    # whereas we want to ignore the edges at the boundary.
    pad_width0 = Hk // 2
    pad_width1 = Wk // 2
    pad_width = ((pad_width0,pad_width0),(pad_width1,pad_width1))
    padded = np.pad(image, pad_width, mode='edge')
    
    for x in range(image.shape[1]):     # Loop over every pixel of the image
        for y in range(image.shape[0]):
            # element-wise multiplication of the kernel and the image
            out[y,x]=np.sum(kernel*padded[y:y + kernel.shape[0], x:x + kernel.shape[1]])

    return out

def gaussian_kernel(size, sigma):
    """ Implementation of Gaussian Kernel.

    This function follows the gaussian kernel formula,
    and creates a kernel matrix.

    Hints:
    - Use np.pi and np.exp to compute pi and exp.

    Args:
        size: int of the size of output matrix.
        sigma: float of sigma to calculate kernel.

    Returns:
        kernel: numpy array of shape (size, size).
    """

    kernel = np.zeros((size, size))
    
    # size = 2k+1 so we calculate k using algebra
    k = (size - 1)/2
    
    #running for loop with i and j to loop over 2D matrix and assign values
    for i in range(size):
        for j in range(size):
            # implementing the formula for gaussian
            kernel[i][j] = (1/(2 * np.pi * sigma**2)) * np.exp((-((i-k)**2 + (j-k)**2))/(2 * (sigma ** 2)))

    return kernel

def partial_x(image):
    """ Computes partial x-derivative of input img.

    Hints:
        - You may use the conv function in defined in this file.

    Args:
        image: numpy array of shape (H, W).
    Returns:
        out: x-derivative image.
    """

    out = None
    I = np.array(image) # converting image into numpy array
    
    kernel = np.array([[-0.5, 0 , 0.5]]) #kernel with 1 row, 3 col 
    out = conv(I, kernel) # convolution function from above

    return out

def partial_y(image):
    """ Computes partial y-derivative of input img.

    Hints:
        - You may use the conv function in defined in this file.

    Args:
        image: numpy array of shape (H, W).
    Returns:
        out: y-derivative image.
    """

    out = None
    
    I = np.array(image)
    
    kernel = np.array([[-0.5], [0], [0.5]]) # kernel with 3 rows , 1 col
    out = conv(I, kernel)
    
    return out

def gradient(image):
    """ Returns gradient magnitude and direction of input img.

    Args:
        image: Grayscale image. Numpy array of shape (H, W).

    Returns:
        G: Magnitude of gradient at each pixel in img.
            Numpy array of shape (H, W).
        theta: Direction(in degrees, 0 <= theta < 360) of gradient
            at each pixel in img. Numpy array of shape (H, W).

    Hints:
        - Use np.sqrt and np.arctan2 to calculate square root and arctan
    """
    
    G = np.zeros(image.shape)
    theta = np.zeros(image.shape)
    
    G = np.sqrt(partial_x(image) ** 2 + partial_y(image) ** 2)
    
    # conversion to degree to make sure the range is between 0 and 360
    theta = (np.rad2deg(np.arctan2(partial_y(image) , partial_x(image)))+180)%360
       
    return G, theta


def non_maximum_suppression(G, theta):
    """ Performs non-maximum suppression.

    This function performs non-maximum suppression along the direction
    of gradient (theta) on the gradient magnitude image (G).

    Args:
        G: gradient magnitude image with shape of (H, W).
        theta: direction of gradients with shape of (H, W).

    Returns:
        out: non-maxima suppressed image.
    """
    H, W = G.shape
    out = np.zeros((H, W))

    # Round the gradient direction to the nearest 45 degrees
    theta = (np.floor((theta + 22.5) / 45) * 45) 
    
    theta = theta % 360# conversion to degree to stay within limits (0,360)

    for i in range(1,H-1):
        for j in range(1,W-1):
            if theta[i,j] == 0 or theta[i,j] == 180:
                 subsequent_val = [G[i,j-1] , G[i,j+1]] #store subsequent pixels
            
            elif theta[i,j] == 45 or theta[i,j] == 225:
                 subsequent_val = [G[i-1,j-1] , G[i+1,j+1]]
            
            elif theta[i,j] == 90 or theta[i,j] == 270:
                 subsequent_val = [G[i-1,j] , G[i+1,j]]
            
            elif theta[i,j] == 135 or theta[i,j] == 315:
                 subsequent_val = [G[i-1,j+1] , G[i+1,j-1]]
            if G[i,j] >= np.max(subsequent_val):# comparison for subsequent pixels
                out[i,j] = G[i,j]
            else:
                out[i,j] = 0
    return out
                 

def double_thresholding(img, high, low):
    """
    Args:
        img: numpy array of shape (H, W) representing NMS edge response.
        high: high threshold(float) for strong edges.
        low: low threshold(float) for weak edges.

    Returns:
        strong_edges: Boolean array which represents strong edges.
            Strong edeges are the pixels with the values greater than
            the higher threshold.
        weak_edges: Boolean array representing weak edges.
            Weak edges are the pixels with the values smaller or equal to the
            higher threshold and greater than the lower threshold.
    """

    strong_edges = np.zeros(img.shape, dtype=np.bool)
    weak_edges = np.zeros(img.shape, dtype=np.bool)
    
    # using boolian algebra to differentiate b/w edges
    strong_edges = img > high
    weak_edges = (img < high) & (img > low)

    return strong_edges, weak_edges


def get_neighbors(y, x, H, W):
    """ Return indices of valid neighbors of (y, x).

    Return indices of all the valid neighbors of (y, x) in an array of
    shape (H, W). An index (i, j) of a valid neighbor should satisfy
    the following:
        1. i >= 0 and i < H
        2. j >= 0 and j < W
        3. (i, j) != (y, x)

    Args:
        y, x: location of the pixel.
        H, W: size of the image.
    Returns:
        neighbors: list of indices of neighboring pixels [(i, j)].
    """
    neighbors = []

    for i in (y-1, y, y+1):
        for j in (x-1, x, x+1):
            if i >= 0 and i < H and j >= 0 and j < W:
                if (i == y and j == x):
                    continue
                neighbors.append((i, j))

    return neighbors

def link_edges(strong_edges, weak_edges):
    """ Find weak edges connected to strong edges and link them.

    Iterate over each pixel in strong_edges and perform breadth first
    search across the connected pixels in weak_edges to link them.
    Here we consider a pixel (a, b) is connected to a pixel (c, d)
    if (a, b) is one of the eight neighboring pixels of (c, d).

    Args:
        strong_edges: binary image of shape (H, W).
        weak_edges: binary image of shape (H, W).
    
    Returns:
        edges: numpy boolean array of shape(H, W).
    """

    H, W = strong_edges.shape
    indices = np.stack(np.nonzero(strong_edges)).T
    edges = np.zeros((H, W), dtype=np.bool)

    # Make new instances of arguments to leave the original
    # references intact
    weak_edges = np.copy(weak_edges)
    edges = np.copy(strong_edges)
    
    traced = np.zeros((H,W))
    
    while len(indices) != 0 : # while stack len not empty
        i,j = indices[0] # equal to first element
        edges[i][j] = True
        
        indices = np.delete(indices,0,axis = 0)
        sub = get_neighbors(i,j,H,W) # get all the subsequent neighbors
       
        for k in sub:
            if weak_edges[k] and not traced[k]: # if element k is not traced already
                traced[k] = True
                indices = np.vstack((indices, k))# stack up in a vertical arr

    return edges

def canny(img, kernel_size=5, sigma=1.4, high=20, low=15):
    """ Implement canny edge detector by calling functions above.

    Args:
        img: binary image of shape (H, W).
        kernel_size: int of size for kernel matrix.
        sigma: float for calculating kernel.
        high: high threshold for strong edges.
        low: low threashold for weak edges.
    Returns:
        edge: numpy array of shape(H, W).
    """
    kernel = gaussian_kernel(kernel_size,sigma)
    img = conv(img,kernel)
    G, theta = gradient(img)
    nms = non_maximum_suppression(G,theta)
    s, w = double_thresholding(nms,high,low)
    edge = link_edges(s,w)
    
    return edge


def hough_transform(img):
    """ Transform points in the input image into Hough space.

    Use the parameterization:
        rho = x * cos(theta) + y * sin(theta)
    to transform a point (x,y) to a sine-like function in Hough space.

    Args:
        img: binary image of shape (H, W).
        
    Returns:
        accumulator: numpy array of shape (m, n).
        rhos: numpy array of shape (m, ).
        thetas: numpy array of shape (n, ).
    """
    # Set rho and theta ranges
    W, H = img.shape
    diag_len = int(np.ceil(np.sqrt(W * W + H * H)))
   
    rhos = np.linspace(-diag_len, diag_len, diag_len * 2 + 1)
    
    thetas = np.deg2rad(np.arange(-90.0, 90.0))

    # Cache some reusable values
    cos_t = np.cos(thetas)
    sin_t = np.sin(thetas)
    num_thetas = len(thetas)

    # Initialize accumulator in the Hough space
    accumulator = np.zeros((2 * diag_len + 1, num_thetas), dtype=np.uint64)
    ys, xs = np.nonzero(img)
    
    for i in range(int(len(xs))):
        for j in range(int(num_thetas)):
            p = int(round(xs[i] + cos_t[j] + ys[i] * sin_t[j]))
            p_n = (np.abs(rhos-p)).argmin()
            accumulator[p_n][j] += 1
    
    

    return accumulator, rhos, thetas
