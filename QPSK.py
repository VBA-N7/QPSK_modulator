import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random


def gen_sin(freq, amp=1, off=0, nb_per=5, res=100):
    end = (1 / freq) * nb_per
    t = np.arange(0.0, end, 1 / (freq * res))
    s = off + amp * np.sin(2 * np.pi * freq * t)
    return t, s


def gen_cos(freq, amp=1, off=0, nb_per=5, res=100):
    end = (1 / freq) * nb_per
    t = np.arange(0.0, end, 1 / (freq * res))
    s = off + amp * np.cos(2 * np.pi * freq * t)
    return t, s


def gen_bin(seq, bit_rate, res=100):
    bin_seq = []
    for char in seq:
        sym = int(char)
        if sym == 0:
            sym = -1
        bin_seq.append(sym)

    bin_signal = []
    for sym in bin_seq:
        s = list(np.full(res, sym))
        bin_signal += s

    end = (1 / bit_rate) * len(bin_seq)
    t = np.arange(0, end, 1 / (bit_rate * res))
    bin_signal = np.array(bin_signal)

    return t, bin_signal


def BPSK(seq, freq_porteuse, bit_rate, res, LO):
    nb_per_needed = (freq_porteuse / baud_rate) * len(seq)

    t1, bin_signal = gen_bin(seq=seq, bit_rate=bit_rate, res=res)
    t2, nus_signal = LO(freq=freq_porteuse, nb_per=nb_per_needed, res=res)

    new_bin_signal = np.interp(t2, t1, bin_signal)

    BPSK = new_bin_signal * nus_signal

    df = pd.DataFrame({'bin_signal': new_bin_signal,
                       'nus_signal': nus_signal,
                       'BPSK': BPSK},
                      index=t2)

    return df


def QPSK(seq, freq_porteuse, bit_rate, res):
    I_seq = seq[0::2]
    Q_seq = seq[1::2]
    I_df = BPSK(I_seq, freq_porteuse, bit_rate, res, gen_cos)
    Q_df = BPSK(Q_seq, freq_porteuse, bit_rate, res, gen_sin)
    QPSK = Q_df['BPSK'] + I_df['BPSK']

    df = pd.DataFrame({'Q_signal': Q_df['BPSK'],
                       'Q_bin_signal': Q_df['bin_signal'],
                       'sinus_signal': Q_df['nus_signal'],
                       'I_signal': I_df['BPSK'],
                       'I_bin_signal': I_df['bin_signal'],
                       'cosinus_signal': I_df['nus_signal'],
                       'QPSK': QPSK},
                      index=Q_df.index)
    return df


# seq = '11000110'  # custom frame
number_of_bit = 16
seq = str(bin(random.randint(0, 2**number_of_bit))[2:])  # random frame

print('Binary sequence modulated: {}'.format(seq))

baud_rate = 1
freq_porteuse = 2


df = BPSK(seq=seq[0::2],
          freq_porteuse=freq_porteuse,
          bit_rate=baud_rate,
          res=100,
          LO=gen_cos)

df1 = BPSK(seq=seq[1::2],
           freq_porteuse=freq_porteuse,
           bit_rate=baud_rate,
           res=100,
           LO=gen_sin)


fig1, ax1 = plt.subplots(2, 2, sharex=True, sharey=True)
fig1.suptitle('I & Q signal for {} data'.format(seq))

ax1[0, 0].plot(df.index, df['nus_signal'], df['bin_signal'])
ax1[0, 0].set_title(seq[0::2])
ax1[0, 0].legend(['cosinus', 'even bits'], loc='lower right')

ax1[1, 0].plot(df.index, df['BPSK'], 'g')
ax1[1, 0].set_title('I_signal')


ax1[0, 1].plot(df1.index, df1['nus_signal'], df1['bin_signal'])
ax1[0, 1].set_title(seq[1::2])
ax1[0, 1].legend(['sinus', 'odd bits'], loc='lower right')

ax1[1, 1].plot(df1.index, df1['BPSK'], 'r')
ax1[1, 1].set_title('Q_signal')


fig2, ax2 = plt.subplots(3, sharex=True)

df2 = QPSK(seq=seq,
           freq_porteuse=freq_porteuse,
           bit_rate=baud_rate,
           res=100)

ax2[0].plot(df2.index, df2['Q_signal'], 'r', df2['Q_bin_signal'], '-k')
ax2[0].legend(['Q_signal',
               'odd bits: {}'.format(seq[1::2])],
              loc='lower right')

ax2[1].plot(df2.index, df2['I_signal'], 'g', df2['I_bin_signal'], '-k')
ax2[1].legend(['I_signal',
               'even bits: {}'.format(seq[0::2])],
              loc='lower right')

ax2[2].plot(df2.index, df2['QPSK'])
ax2[2].legend(['QPSK'], loc='lower right')

for axes in ax2:
    axes.grid(which='both')

fig2.suptitle('I & Q signal and QPSK for {} data'.format(seq))

plt.show()
