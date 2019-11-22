from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import random

import rnn
import numpy as np
import tensorflow as tf


def copy_hparams(hparams):
    """Return a copy of an HParams instance."""
    return tf.contrib.training.HParams(**hparams.values())


def get_default_hparams():
    """Return default HParams for sketch-rnn."""
    hparams = tf.contrib.training.HParams(
        data_set=['cat.npz'],  # Our dataset.
        num_steps=10000000,  # Total number of steps of training. Keep large.
        save_every=2000,  # Number of batches per checkpoint creation.
        img_H=48,
        img_W=48,
        max_seq_len=250,  # Not used. Will be changed by model. [Eliminate?]
        dec_rnn_size=512,  # Size of decoder.
        dec_model='hyper',  # Decoder: lstm, layer_norm or hyper.
        z_size=128,  # Size of latent vector z. Recommend 32, 64 or 128.
        batch_size=100,  # Minibatch size. Recommend leaving at 100.
        grad_clip=1.0,  # Gradient clipping. Recommend leaving at 1.0.
        num_mixture=20,  # Number of mixtures in Gaussian mixture model.
        learning_rate=0.001,  # Learning rate.
        decay_rate=0.9999,  # Learning rate decay per minibatch.
        min_learning_rate=0.00001,  # Minimum learning rate.
        use_recurrent_dropout=True,  # Dropout with memory loss. Recommended
        recurrent_dropout_prob=0.90,  # Probability of recurrent dropout keep.
        use_input_dropout=False,  # Input dropout. Recommend leaving False.
        input_dropout_prob=0.90,  # Probability of input dropout keep.
        use_output_dropout=False,  # Output dropout. Recommend leaving False.
        output_dropout_prob=0.90,  # Probability of output dropout keep.
        random_scale_factor=0.15,  # Random scaling data augmentation proportion.
        augment_stroke_prob=0.10,  # Point dropping augmentation proportion.
        conditional=True,  # When False, use unconditional decoder-only model.
        is_training=True  # Is model training? Recommend keeping true.
    )
    return hparams


class Model(object):
    """Define a SketchRNN model."""

    def __init__(self, hps, gpu_mode=True, reuse=False):
        """Initializer for the SketchRNN model.

    Args:
       hps: a HParams object containing model hyperparameters
       gpu_mode: a boolean that when True, uses GPU mode.
       reuse: a boolean that when true, attemps to reuse variables.
    """
        self.hps = hps
        with tf.variable_scope('vector_rnn', reuse=reuse):
            if not gpu_mode:
                with tf.device('/cpu:0'):
                    print('Model using cpu.')
                    self.build_model(hps)
            else:
                print('-' * 100)
                print('is_training:', hps.is_training)
                print('Model using gpu.')
                self.build_model(hps)

    def stride_arr(self, stride):
        """Map a stride scalar to the stride array for tf.nn.conv2d."""
        return [1, stride, stride, 1]

    def high_pass_filtering(self, img_in):
        """
        high pass filtering
        :param img_in: [N, H, W, 1]
        :return: img_out: [N, H, W, 1]
        """
        filter_hp = tf.constant([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]], tf.float32)
        filter_hp = tf.expand_dims(tf.expand_dims(filter_hp, -1), -1, name='hp_w')  # [3, 3, 1, 1]
        img_out = tf.nn.conv2d(img_in, filter_hp, strides=self.stride_arr(1), padding='SAME')
        return img_out

    def conv_2d(self, name, x, filter_size, out_filters, strides, padding='SAME'):
        with tf.variable_scope(name):
            in_filters = int(x.get_shape()[-1])
            n = filter_size * filter_size * out_filters
            w = tf.get_variable(name='DW', shape=[filter_size, filter_size, in_filters, out_filters], dtype=tf.float32,
                                initializer=tf.random_normal_initializer(stddev=np.sqrt(2.0 / n)))
            conv = tf.nn.conv2d(x, w, strides, padding=padding)
            return conv

    def cnn_encoder(self, img_x):
        with tf.variable_scope('ENC_CNN'):
            # high-pass filter
            x = self.high_pass_filtering(img_x)  # [N, 48, 48, 1]

            # 6 conv layers
            x = self.conv_2d('conv1', x, filter_size=2, out_filters=4, strides=self.stride_arr(2))  # [N, 24, 24, 4]
            x = tf.nn.relu(x)
            x = self.conv_2d('conv2', x, filter_size=2, out_filters=4, strides=self.stride_arr(1))  # [N, 24, 24, 4]
            x = tf.nn.relu(x)
            x = self.conv_2d('conv3', x, filter_size=2, out_filters=8, strides=self.stride_arr(2))  # [N, 12, 12, 8]
            x = tf.nn.relu(x)
            x = self.conv_2d('conv4', x, filter_size=2, out_filters=8, strides=self.stride_arr(1))  # [N, 12, 12, 8]
            x = tf.nn.relu(x)
            x = self.conv_2d('conv5', x, filter_size=2, out_filters=8, strides=self.stride_arr(2))  # [N, 6, 6, 8]
            x = tf.nn.relu(x)
            x = self.conv_2d('conv6', x, filter_size=2, out_filters=8, strides=self.stride_arr(1))  # [N, 6, 6, 8]
            x = tf.tanh(x)

            x = tf.reshape(x, shape=[x.shape[0], -1])  # [N, 6 * 6 * 8]

            mu = rnn.super_linear(
                x,
                self.hps.z_size,
                scope='ENC_CNN_mu',
                init_w='gaussian',
                weight_start=0.001)
            presig = rnn.super_linear(
                x,
                self.hps.z_size,
                scope='ENC_CNN_sigma',
                init_w='gaussian',
                weight_start=0.001)
            return mu, presig

    def build_model(self, hps):
        """Define model architecture."""
        if hps.is_training:
            self.global_step = tf.Variable(0, name='global_step', trainable=False)

        if hps.dec_model == 'lstm':
            cell_fn = rnn.LSTMCell
        elif hps.dec_model == 'layer_norm':
            cell_fn = rnn.LayerNormLSTMCell
        elif hps.dec_model == 'hyper':
            cell_fn = rnn.HyperLSTMCell
        else:
            assert False, 'please choose a respectable cell'

        use_recurrent_dropout = self.hps.use_recurrent_dropout
        use_input_dropout = self.hps.use_input_dropout
        use_output_dropout = self.hps.use_output_dropout

        cell = cell_fn(
            hps.dec_rnn_size,
            use_recurrent_dropout=use_recurrent_dropout,
            dropout_keep_prob=self.hps.recurrent_dropout_prob)

        # dropout:
        print('Input dropout mode = %s.' % use_input_dropout)
        print('Output dropout mode = %s.' % use_output_dropout)
        print('Recurrent dropout mode = %s.' % use_recurrent_dropout)
        if use_input_dropout:
            print('Dropout to input w/ keep_prob = %4.4f.' % self.hps.input_dropout_prob)
            cell = tf.contrib.rnn.DropoutWrapper(
                cell, input_keep_prob=self.hps.input_dropout_prob)
        if use_output_dropout:
            print('Dropout to output w/ keep_prob = %4.4f.' % self.hps.output_dropout_prob)
            cell = tf.contrib.rnn.DropoutWrapper(
                cell, output_keep_prob=self.hps.output_dropout_prob)
        self.cell = cell

        # self.sequence_lengths = tf.placeholder(
        #     dtype=tf.int32, shape=[self.hps.batch_size])
        self.input_data = tf.placeholder(
            dtype=tf.float32,
            shape=[self.hps.batch_size, self.hps.max_seq_len + 1, 5])

        # extra input: pixelwise sketch
        self.input_image = tf.placeholder(
            dtype=tf.float32,
            shape=[self.hps.batch_size, self.hps.img_H, self.hps.img_W, 1])

        # The target/expected vectors of strokes
        self.output_x = self.input_data[:, 1:self.hps.max_seq_len + 1, :]  # [N, max_seq_len, 5]
        # vectors of strokes to be fed to decoder (same as above, but lagged behind
        # one step to include initial dummy value of (0, 0, 1, 0, 0))
        self.input_x = self.input_data[:, :self.hps.max_seq_len, :]  # [N, max_seq_len, 5]

        # either do vae-bit and get z, or do unconditional, decoder-only
        if hps.conditional:  # vae mode:
            self.mean, self.presig = self.cnn_encoder(self.input_image)

            self.sigma = tf.exp(self.presig / 2.0)  # sigma > 0. div 2.0 -> sqrt.
            eps = tf.random_normal(
                (self.hps.batch_size, self.hps.z_size), 0.0, 1.0, dtype=tf.float32)
            self.batch_z = self.mean + tf.multiply(self.sigma, eps)  # [N, z_size]

            pre_tile_y = tf.reshape(self.batch_z,
                                    [self.hps.batch_size, 1, self.hps.z_size])
            overlay_x = tf.tile(pre_tile_y, [1, self.hps.max_seq_len, 1])  # [N, max_seq_len, z_size]
            actual_input_x = tf.concat([self.input_x, overlay_x], 2)

            self.initial_state = tf.nn.tanh(
                rnn.super_linear(
                    self.batch_z,
                    cell.state_size,
                    init_w='gaussian',
                    weight_start=0.001,
                    input_size=self.hps.z_size))
        else:  # unconditional, decoder-only generation
            self.batch_z = tf.zeros(
                (self.hps.batch_size, self.hps.z_size), dtype=tf.float32)
            actual_input_x = self.input_x
            self.initial_state = cell.zero_state(
                batch_size=hps.batch_size, dtype=tf.float32)

        self.num_mixture = hps.num_mixture

        # TODO(deck): Better understand this comment.
        # Number of outputs is 3 (one logit per pen state) plus 6 per mixture
        # component: mean_x, stdev_x, mean_y, stdev_y, correlation_xy, and the
        # mixture weight/probability (Pi_k)
        n_out = (3 + self.num_mixture * 6)

        with tf.variable_scope('RNN'):
            output_w = tf.get_variable('output_w', [self.hps.dec_rnn_size, n_out])
            output_b = tf.get_variable('output_b', [n_out])

        # decoder module of sketch-rnn is below
        output, last_state = tf.nn.dynamic_rnn(
            cell,
            actual_input_x,
            initial_state=self.initial_state,
            time_major=False,
            swap_memory=True,
            dtype=tf.float32,
            scope='RNN')

        output = tf.reshape(output, [-1, hps.dec_rnn_size])
        output = tf.nn.xw_plus_b(output, output_w, output_b)
        self.final_state = last_state

        # NB: the below are inner functions, not methods of Model
        def tf_2d_normal(x1, x2, mu1, mu2, s1, s2, rho):
            """Returns result of eq # 24 of http://arxiv.org/abs/1308.0850."""
            norm1 = tf.subtract(x1, mu1)
            norm2 = tf.subtract(x2, mu2)
            s1s2 = tf.multiply(s1, s2)
            # eq 25
            z = (tf.square(tf.div(norm1, s1)) + tf.square(tf.div(norm2, s2)) -
                 2 * tf.div(tf.multiply(rho, tf.multiply(norm1, norm2)), s1s2))
            neg_rho = 1 - tf.square(rho)
            result = tf.exp(tf.div(-z, 2 * neg_rho))
            denom = 2 * np.pi * tf.multiply(s1s2, tf.sqrt(neg_rho))
            result = tf.div(result, denom)
            return result

        def get_lossfunc(z_pi, z_mu1, z_mu2, z_sigma1, z_sigma2, z_corr,
                         z_pen_logits, x1_data, x2_data, pen_data):
            """Returns a loss fn based on eq #26 of http://arxiv.org/abs/1308.0850."""
            # This represents the L_R only (i.e. does not include the KL loss term).

            result0 = tf_2d_normal(x1_data, x2_data, z_mu1, z_mu2, z_sigma1, z_sigma2,
                                   z_corr)
            epsilon = 1e-6
            # result1 is the loss wrt pen offset (L_s in equation 9 of
            # https://arxiv.org/pdf/1704.03477.pdf)
            result1 = tf.multiply(result0, z_pi)
            result1 = tf.reduce_sum(result1, 1, keep_dims=True)
            result1 = -tf.log(result1 + epsilon)  # avoid log(0)

            fs = 1.0 - pen_data[:, 2]  # use training data for this
            fs = tf.reshape(fs, [-1, 1])
            # Zero out loss terms beyond N_s, the last actual stroke
            result1 = tf.multiply(result1, fs)

            # result2: loss wrt pen state, (L_p in equation 9)
            result2 = tf.nn.softmax_cross_entropy_with_logits(
                labels=pen_data, logits=z_pen_logits)
            result2 = tf.reshape(result2, [-1, 1])
            if not self.hps.is_training:  # eval mode, mask eos columns
                result2 = tf.multiply(result2, fs)

            result = result1 + result2
            return result

        # below is where we need to do MDN (Mixture Density Network) splitting of
        # distribution params
        def get_mixture_coef(output):
            """Returns the tf slices containing mdn dist params."""
            # This uses eqns 18 -> 23 of http://arxiv.org/abs/1308.0850.
            z = output
            z_pen_logits = z[:, 0:3]  # pen states
            z_pi, z_mu1, z_mu2, z_sigma1, z_sigma2, z_corr = tf.split(z[:, 3:], 6, 1)

            # process output z's into MDN parameters

            # softmax all the pi's and pen states:
            z_pi = tf.nn.softmax(z_pi)
            z_pen = tf.nn.softmax(z_pen_logits)

            # exponentiate the sigmas and also make corr between -1 and 1.
            z_sigma1 = tf.exp(z_sigma1)
            z_sigma2 = tf.exp(z_sigma2)
            z_corr = tf.tanh(z_corr)

            r = [z_pi, z_mu1, z_mu2, z_sigma1, z_sigma2, z_corr, z_pen, z_pen_logits]
            return r

        out = get_mixture_coef(output)
        [o_pi, o_mu1, o_mu2, o_sigma1, o_sigma2, o_corr, o_pen, o_pen_logits] = out

        self.pi = o_pi
        self.mu1 = o_mu1
        self.mu2 = o_mu2
        self.sigma1 = o_sigma1
        self.sigma2 = o_sigma2
        self.corr = o_corr
        self.pen_logits = o_pen_logits
        # pen state probabilities (result of applying softmax to self.pen_logits)
        self.pen = o_pen

        # reshape target data so that it is compatible with prediction shape
        target = tf.reshape(self.output_x, [-1, 5])
        [x1_data, x2_data, eos_data, eoc_data, cont_data] = tf.split(target, 5, 1)
        pen_data = tf.concat([eos_data, eoc_data, cont_data], 1)

        lossfunc = get_lossfunc(o_pi, o_mu1, o_mu2, o_sigma1, o_sigma2, o_corr,
                                o_pen_logits, x1_data, x2_data, pen_data)

        self.r_cost = tf.reduce_mean(lossfunc)

        if self.hps.is_training:
            self.lr = tf.Variable(self.hps.learning_rate, trainable=False)
            optimizer = tf.train.AdamOptimizer(self.lr)

            self.cost = self.r_cost

            gvs = optimizer.compute_gradients(self.cost)
            g = self.hps.grad_clip
            capped_gvs = [(tf.clip_by_value(grad, -g, g), var) for grad, var in gvs]
            self.train_op = optimizer.apply_gradients(
                capped_gvs, global_step=self.global_step, name='train_step')


def sample(sess, model, seq_len=250, temperature=1.0, greedy_mode=False,
           z=None):
    """Samples a sequence from a pre-trained model."""

    def adjust_temp(pi_pdf, temp):
        pi_pdf = np.log(pi_pdf) / temp
        pi_pdf -= pi_pdf.max()
        pi_pdf = np.exp(pi_pdf)
        pi_pdf /= pi_pdf.sum()
        return pi_pdf

    def get_pi_idx(x, pdf, temp=1.0, greedy=False):
        """Samples from a pdf, optionally greedily."""
        if greedy:
            return np.argmax(pdf)
        pdf = adjust_temp(np.copy(pdf), temp)
        accumulate = 0
        for i in range(0, pdf.size):
            accumulate += pdf[i]
            if accumulate >= x:
                return i
        print('Error with sampling ensemble.')
        return -1

    def sample_gaussian_2d(mu1, mu2, s1, s2, rho, temp=1.0, greedy=False):
        if greedy:
            return mu1, mu2
        mean = [mu1, mu2]
        s1 *= temp * temp
        s2 *= temp * temp
        cov = [[s1 * s1, rho * s1 * s2], [rho * s1 * s2, s2 * s2]]
        x = np.random.multivariate_normal(mean, cov, 1)
        return x[0][0], x[0][1]

    prev_x = np.zeros((1, 1, 5), dtype=np.float32)
    prev_x[0, 0, 2] = 1  # S0: [0, 0, 1, 0, 0]
    if z is None:
        z = np.random.randn(1, model.hps.z_size)  # not used if unconditional

    if not model.hps.conditional:
        prev_state = sess.run(model.initial_state)
    else:
        prev_state = sess.run(model.initial_state, feed_dict={model.batch_z: z})

    strokes = np.zeros((seq_len, 5), dtype=np.float32)
    mixture_params = []

    temp = temperature

    for i in range(seq_len):
        if not model.hps.conditional:
            feed = {
                model.input_x: prev_x,
                model.initial_state: prev_state
            }
        else:
            feed = {
                model.input_x: prev_x,
                model.initial_state: prev_state,
                model.batch_z: z
            }

        params = sess.run([
            model.pi, model.mu1, model.mu2, model.sigma1, model.sigma2, model.corr,
            model.pen, model.final_state
        ], feed)

        # top 6 param: [1, 20], o_pen: [1, 3], next_state: [1, 1024]
        [o_pi, o_mu1, o_mu2, o_sigma1, o_sigma2, o_corr, o_pen, next_state] = params

        idx = get_pi_idx(random.random(), o_pi[0], temp, greedy_mode)

        idx_eos = get_pi_idx(random.random(), o_pen[0], temp, greedy_mode)

        eos = [0, 0, 0]
        eos[idx_eos] = 1

        next_x1, next_x2 = sample_gaussian_2d(o_mu1[0][idx], o_mu2[0][idx],
                                              o_sigma1[0][idx], o_sigma2[0][idx],
                                              o_corr[0][idx], np.sqrt(temp), greedy_mode)

        strokes[i, :] = [next_x1, next_x2, eos[0], eos[1], eos[2]]

        params = [
            o_pi[0], o_mu1[0], o_mu2[0], o_sigma1[0], o_sigma2[0], o_corr[0],
            o_pen[0]
        ]

        mixture_params.append(params)

        prev_x = np.zeros((1, 1, 5), dtype=np.float32)
        prev_x[0][0] = np.array(
            [next_x1, next_x2, eos[0], eos[1], eos[2]], dtype=np.float32)
        prev_state = next_state

    return strokes, mixture_params
