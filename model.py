from keras.models import Model
from keras.layers import Conv2D, MaxPooling2D, UpSampling2D, Concatenate, Input

def conv_block(input_tensor, num_filters):
    x = Conv2D(num_filters, (3, 3), padding='same', activation='relu')(input_tensor)
    x = Conv2D(num_filters, (3, 3), padding='same', activation='relu')(x)
    return x

def build_model(input_height, input_width, num_channels):
    inputs = Input(shape=(input_height, input_width, num_channels))

    # Encoder
    conv1 = conv_block(inputs, 64)
    pool1 = MaxPooling2D(pool_size=(2, 2))(conv1)

    conv2 = conv_block(pool1, 128)
    pool2 = MaxPooling2D(pool_size=(2, 2))(conv2)

    conv3 = conv_block(pool2, 256)
    pool3 = MaxPooling2D(pool_size=(2, 2))(conv3)

    conv4 = conv_block(pool3, 512)
    pool4 = MaxPooling2D(pool_size=(2, 2))(conv4)

    # Bottleneck
    conv5 = conv_block(pool4, 1024)

    # Decoder
    up6 = Concatenate(axis=3)([UpSampling2D(size=(2, 2))(conv5), conv4])
    conv6 = conv_block(up6, 512)

    up7 = Concatenate(axis=3)([UpSampling2D(size=(2, 2))(conv6), conv3])
    conv7 = conv_block(up7, 256)

    up8 = Concatenate(axis=3)([UpSampling2D(size=(2, 2))(conv7), conv2])
    conv8 = conv_block(up8, 128)

    up9 = Concatenate(axis=3)([UpSampling2D(size=(2, 2))(conv8), conv1])
    conv9 = conv_block(up9, 64)

    # Output layer
    outputs = Conv2D(1, (1, 1), activation='linear')(conv9)

    return Model(inputs=inputs, outputs=outputs)

import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Conv2D, UpSampling2D, Concatenate, Input
from efficientnet.tfkeras import EfficientNetB0

def build_efficientnet_model(input_height, input_width, num_channels):
    inputs = Input(shape=(input_height, input_width, num_channels))

    # Encoder (EfficientNet)
    base_model = EfficientNetB0(weights='imagenet', include_top=False, input_tensor=inputs)
    base_layers = [base_model.get_layer(name).output for name in ['block2a_expand_activation', 'block3a_expand_activation', 'block4a_expand_activation', 'block6a_expand_activation', 'top_activation']]
    
    # Decoder
    up1 = Concatenate(axis=3)([UpSampling2D(size=(2, 2))(base_layers[4]), base_layers[3]])
    conv1 = Conv2D(256, (3, 3), padding='same', activation='relu')(up1)

    up2 = Concatenate(axis=3)([UpSampling2D(size=(2, 2))(conv1), base_layers[2]])
    conv2 = Conv2D(128, (3, 3), padding='same', activation='relu')(up2)

    up3 = Concatenate(axis=3)([UpSampling2D(size=(2, 2))(conv2), base_layers[1]])
    conv3 = Conv2D(64, (3, 3), padding='same', activation='relu')(up3)

    up4 = Concatenate(axis=3)([UpSampling2D(size=(2, 2))(conv3), base_layers[0]])
    conv4 = Conv2D(32, (3, 3), padding='same', activation='relu')(up4)

    # Output layer
    outputs = Conv2D(1, (1, 1), activation='linear')(conv4)

    return Model(inputs=inputs, outputs=outputs)
