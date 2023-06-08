import os
import logging

import numpy as np
import svgwrite

import drawing
import lyrics
from rnn import rnn
from datetime import datetime

import sys

from itertools import chain

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ["TUNE_DISABLE_AUTO_CALLBACK_LOGGERS"] = "1"


class Hand(object):

    def __init__(self):
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
        self.nn = rnn(
            log_dir='logs',
            checkpoint_dir='checkpoints',
            prediction_dir='predictions',
            learning_rates=[.0001, .00005, .00002],
            # batch_sizes=[32, 64, 64],
            batch_sizes=[1024, 2048, 2048],
            patiences=[1500, 1000, 500],
            beta1_decays=[.9, .9, .9],
            # validation_batch_size=32,
            validation_batch_size=1024,
            optimizer='rms',
            num_training_steps=100000,
            warm_start_init_step=17900,
            regularization_constant=0.0,
            keep_prob=1.0,
            enable_parameter_averaging=False,
            min_steps_to_checkpoint=2000,
            log_interval=20,
            logging_level=logging.CRITICAL,
            grad_clip=10,
            lstm_size=400,
            output_mixture_components=20,
            attention_mixture_components=10
        )
        self.nn.restore()

    def write(self, filename, lines, biases=None, styles=None, stroke_colors=None, stroke_widths=None):
        valid_char_set = set(drawing.alphabet)
        for line_num, line in enumerate(lines):
            if len(line) > 75:
                raise ValueError(
                    (
                        "Each line must be at most 75 characters. "
                        "Line {} contains {}"
                    ).format(line_num, len(line))
                )

            for char in line:
                if char not in valid_char_set:
                    raise ValueError(
                        (
                            "Invalid character {} detected in line {}. "
                            "Valid character set is {}"
                        ).format(char, line_num, valid_char_set)
                    )

        strokes = self._sample(lines, biases=biases, styles=styles)
        self._draw(strokes, lines, filename, stroke_colors=stroke_colors, stroke_widths=stroke_widths)

    def _sample(self, lines, biases=None, styles=None):
        num_samples = len(lines)
        max_tsteps = 40*max([len(i) for i in lines])
        biases = biases if biases is not None else [0.5]*num_samples

        x_prime = np.zeros([num_samples, 1200, 3])
        x_prime_len = np.zeros([num_samples])
        chars = np.zeros([num_samples, 120])
        chars_len = np.zeros([num_samples])

        if styles is not None:
            for i, (cs, style) in enumerate(zip(lines, styles)):
                x_p = np.load('styles/style-{}-strokes.npy'.format(style))
                c_p = np.load('styles/style-{}-chars.npy'.format(style)).tostring().decode('utf-8')

                c_p = str(c_p) + " " + cs
                c_p = drawing.encode_ascii(c_p)
                c_p = np.array(c_p)

                x_prime[i, :len(x_p), :] = x_p
                x_prime_len[i] = len(x_p)
                chars[i, :len(c_p)] = c_p
                chars_len[i] = len(c_p)

        else:
            for i in range(num_samples):
                encoded = drawing.encode_ascii(lines[i])
                chars[i, :len(encoded)] = encoded
                chars_len[i] = len(encoded)

        [samples] = self.nn.session.run(
            [self.nn.sampled_sequence],
            feed_dict={
                self.nn.prime: styles is not None,
                self.nn.x_prime: x_prime,
                self.nn.x_prime_len: x_prime_len,
                self.nn.num_samples: num_samples,
                self.nn.sample_tsteps: max_tsteps,
                self.nn.c: chars,
                self.nn.c_len: chars_len,
                self.nn.bias: biases
            }
        )
        samples = [sample[~np.all(sample == 0.0, axis=1)] for sample in samples]
        return samples

    def _draw(self, strokes, lines, filename, stroke_colors=None, stroke_widths=None):
        stroke_colors = stroke_colors or ['black']*len(lines)
        stroke_widths = stroke_widths or [2]*len(lines)


        ############################################################################################################
        #line_height = 60
        line_height = 45
        view_width = 1000
        view_height = line_height*(len(strokes) + 1)

        dwg = svgwrite.Drawing(filename=filename)
        dwg.viewbox(width=view_width, height=view_height)
        dwg.add(dwg.rect(insert=(0, 0), size=(view_width, view_height), fill='white'))

        initial_coord = np.array([0, -(3*line_height / 4)])
        for offsets, line, color, width in zip(strokes, lines, stroke_colors, stroke_widths):

            if not line:
                initial_coord[1] -= line_height
                continue

            offsets[:, :2] *= 1.5
            strokes = drawing.offsets_to_coords(offsets)
            strokes = drawing.denoise(strokes)
            strokes[:, :2] = drawing.align(strokes[:, :2])

            strokes[:, 1] *= -1
            strokes[:, :2] -= strokes[:, :2].min() + initial_coord
            # Uncomment below to align to the middle
            # strokes[:, 0] += (view_width - strokes[:, 0].max()) / 2

            prev_eos = 1.0
            p = "M{},{} ".format(0, 0)
            for x, y, eos in zip(*strokes.T):
                p += '{}{},{} '.format('M' if prev_eos == 1.0 else 'L', x, y)
                prev_eos = eos
            path = svgwrite.path.Path(p)
            path = path.stroke(color=color, width=width, linecap='round').fill("none")
            dwg.add(path)

            initial_coord[1] -= line_height

        dwg.save()


def synth(text, style=5, bias=2.4, filename='paths'):
    init_time = datetime.now()
    timestamp = datetime.timestamp(init_time)

    hexstamp = hex(int(timestamp)).lstrip("0x").rstrip("L")

    #filename_path = f'img/{filename}/{filename}-S{style}-B{int(bias*10)}-{hexstamp}.svg'
    filename_path = 'img/'+filename+'/'+filename+'-S'+str(style)+'-B'+str(int(bias*10))+'-'+hexstamp+'.svg'

    if not os.path.exists('img/'+filename):
        print('os.path doesnt exist')
        os.makedirs('img/'+filename)
        print('os.path img/'+filename+' was created')

    hand = Hand()

    newline = []

    try:
        lines = text.split("\n")
    except:
        lines=[text]

    # try:
    #     lines_n = text.split("\n")
    #     for i in lines:
    #         try:
    #             newline.append(0)
    #             i.split("  ")
    #             for s in i:
    #                 newline[-1] += 1
    #         except:
    #             pass
    #     lines = list(chain.from_iterable(lines))
    # except:
    #     lines=[text]
    

    biases = [bias for i in lines]
    styles = [style for i in lines]
    
    hand.write(
        filename=filename_path,
        lines=lines,
        biases=biases,
        styles=styles,
    )

    exec_time = (datetime.now()-init_time)
    print('Generated in '+str(exec_time.seconds)+' seconds.')
    return filename_path, newline

if __name__ == '__main__':
    print(sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), sys.argv[4])
    synth(sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), sys.argv[4])
    
