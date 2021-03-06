# coding: utf-8
import cPickle
import gzip
import os
import sys
import time
import pdb

import numpy

import theano
import theano.tensor as T




class LogisticRegression(object):
    """Multi-class Logistic Regression Class

    The logistic regression is fully described by a weight matrix :math:`W`
    and bias vector :math:`b`. Classification is done by projecting data
    points onto a set of hyperplanes, the distance to which is used to
    determine a class membership probability.
    """

    def __init__(self, input, n_in, n_out, y_type, W=None, b=None):
        """ Initialize the parameters of the logistic regression

        :param input: symbolic variable that describes the input of the
                      architecture (one minibatch)

        :param n_in: number of input units, the dimension of the space in
                     which the datapoints lie

        :param n_out: number of output units, the dimension of the space in
                      which the labels lie

        :param y_type: 0: regression
                       1: sigmoid
                       2: softmax
        """

        # initialize with 0 the weights W as a matrix of shape (n_in, n_out)
        if W is None:
            self.W = theano.shared(value=numpy.zeros((n_in, n_out),
                                                     dtype=theano.config.floatX),
                                    name='W', borrow=True)
        else:
            self.W = W
        # initialize the baises b as a vector of n_out 0s
        if b is None:
            self.b = theano.shared(value=numpy.zeros((n_out,),
                                                     dtype=theano.config.floatX),
                                   name='b', borrow=True)
        else:
            self.b = b
        # compute vector of class-membership probabilities in symbolic form
        
        if y_type == 0:  ###   regression
            self.p_y_given_x = T.dot(input, self.W) + self.b
            self.y_pred = self.p_y_given_x

        # elif y_type == 1:  ###   binary classification
        #     self.p_y_given_x = T.nnet.sigmoid(T.dot(input, self.W) + self.b)
        #     self.y_pred = T.round(self.p_y_given_x) 

        else:  ###   multi-label classification
            self.p_y_given_x = T.nnet.softmax(T.dot(input, self.W) + self.b)
            self.y_pred = T.argmax(self.p_y_given_x,axis=1)

        # parameters of the model
        self.params = [self.W, self.b]

    def negative_log_likelihood(self, y):
        """Return the mean of the negative log-likelihood of the prediction
        of this model under a given target distribution.

        .. math::

            \frac{1}{|\mathcal{D}|} \mathcal{L} (\theta=\{W,b\}, \mathcal{D}) =
            \frac{1}{|\mathcal{D}|} \sum_{i=0}^{|\mathcal{D}|} \log(P(Y=y^{(i)}|x^{(i)}, W,b)) \\
                \ell (\theta=\{W,b\}, \mathcal{D})

        :type y: theano.tensor.TensorType
        :param y: corresponds to a vector that gives for each example the
                  correct label

        Note: we use the mean instead of the sum so that
              the learning rate is less dependent on the batch size
        """
        # y.shape[0] is (symbolically) the number of rows in y, i.e.,
        # number of examples (call it n) in the minibatch
        # T.arange(y.shape[0]) is a symbolic vector which will contain
        # [0,1,2,... n-1] T.log(self.p_y_given_x) is a matrix of
        # Log-Probabilities (call it LP) with one row per example and
        # one column per class LP[T.arange(y.shape[0]),y] is a vector
        # v containing [LP[0,y[0]], LP[1,y[1]], LP[2,y[2]], ...,
        # LP[n-1,y[n-1]]] and T.mean(LP[T.arange(y.shape[0]),y]) is
        # the mean (across minibatch examples) of the elements in v,
        # i.e., the mean log-likelihood across the minibatch.
        return -T.mean(T.log(self.p_y_given_x)[T.arange(y.shape[0]), y])


    def squared_error(self, y):
        return T.mean((y - self.p_y_given_x) ** 2)

    def cross_entropy(self, y):
        return - T.mean(T.sum(y * T.log(self.p_y_given_x) + (1 - y) * T.log(1 - self.p_y_given_x), axis=1))

    def errors(self, y):
        """Return a float representing the number of errors in the minibatch
        over the total number of examples of the minibatch ; zero one
        loss over the size of the minibatch

        :type y: theano.tensor.TensorType
        :param y: corresponds to a vector that gives for each example the
                  correct label
        """
        # check if y has same dimension of y_pred
        if y.ndim != self.y_pred.ndim:
            pdb.set_trace()
            raise TypeError('y should have the same shape as self.y_pred',
                ('y', y.type, 'y_pred', self.y_pred.type))
            # check if y is of the correct datatype
        if y.dtype.startswith('int'):
            # the T.neq operator returns a vector of 0s and 1s, where 1
            # represents a mistake in prediction
	    return T.mean(T.neq(self.y_pred, y))
        else:
            # return T.mean((self.y_pred - y) ** 2)
            return T.mean(T.neq(self.y_pred <= 0, y <= 0))

