import tensorflow as tf

class Autoencoder:
    @staticmethod
    def weight_variable(shape, name):
        initial = tf.truncated_normal(shape, stddev=0.1)
        return tf.Variable(initial, name=name)

    @staticmethod
    def bias_variable(shape, name):
        initial = tf.constant(0.1, shape=shape)
        return tf.Variable(initial, name=name)

    @staticmethod
    def fc_layer(previous, input_size, output_size, name):
        W = Autoencoder.weight_variable([input_size, output_size], name + '_W')
        b = Autoencoder.bias_variable([output_size], name + '_b')
        return tf.add(tf.matmul(previous, W), b, name=name)

    @staticmethod
    def encoder(x, encoding_size):
        l1 = tf.nn.tanh(Autoencoder.fc_layer(x, x.get_shape().as_list()[1], 50, 'encoder_1'))
        l2 = tf.nn.tanh(Autoencoder.fc_layer(l1, 50, 50, 'encoder_2'))
        l3 = tf.nn.tanh(Autoencoder.fc_layer(l2, 50, encoding_size, 'encoder_3'), name="Encoded")
        return l3

    @staticmethod
    def decoder(encoded, out_size):
        l4 = tf.nn.tanh(Autoencoder.fc_layer(encoded, encoded.get_shape().as_list()[1], 50, 'decoder_1'))
        l5 = tf.nn.tanh(Autoencoder.fc_layer(l4, 50, 50, 'decoder_2'))
        out = tf.nn.relu(Autoencoder.fc_layer(l5, 50, out_size, 'decoder_3'), name="Decoded")
        return out

    @staticmethod
    def discriminator(x):
        l1 = tf.nn.tanh(Autoencoder.fc_layer(x, x.get_shape().as_list()[1], 50, 'discriminator_1'))
        l2 = tf.nn.tanh(Autoencoder.fc_layer(l1, 50, 50, 'discriminator_2',))
        l3 = tf.nn.tanh(Autoencoder.fc_layer(l2, 50, 1, 'discriminator_3'), name="Discriminated")
        return l3

    @staticmethod
    def autoencoder(x):
        encoded = Autoencoder.encoder(x, 2)
        decoded = Autoencoder.decoder(encoded, x.get_shape().as_list()[1])
        loss = tf.reduce_mean(tf.squared_difference(x, decoded), name="Loss")
        return loss, decoded, encoded

    @staticmethod
    def add_noise(x, mean, stddev):
        noise = tf.random_normal(shape=tf.shape(x), mean=mean, stddev=stddev)
        return x + noise

    @staticmethod
    def gancoder(x):
        encoded = Autoencoder.encoder(x, 2)
        decoded = Autoencoder.decoder(encoded, x.get_shape().as_list()[1])

        to_discriminate = tf.concat([x, decoded], 0)
        discriminated = Autoencoder.discriminator(to_discriminate)
        num_inputs = tf.shape(x)[0]
        num_decodes = tf.shape(decoded)[0]
        discrimination_labels = tf.concat([tf.ones([num_inputs, 1]), 0 - tf.ones([num_decodes, 1])], 0)

        discriminator_loss = tf.reduce_mean(tf.squared_difference(discrimination_labels, discriminated))
        generator_loss = tf.reduce_mean(tf.squared_difference(x, decoded), name="GenLoss")
        return generator_loss, discriminator_loss, decoded, encoded, discriminated
