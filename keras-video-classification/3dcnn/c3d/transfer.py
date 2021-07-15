from keras.layers import Dense, Dropout
from tensorflow.keras.models import Model

from sport1m_model import create_model_functional, create_features_exctractor


def main():
    model = create_model_functional()
    try:
        model.load_weights('/Users/tom/Downloads/C3D_Sport1M_weights_keras_2.2.4.h5')
    except OSError as err:
        print('Check path to the model weights\' file!\n\n', err)

    baseModel = create_features_exctractor(model)
    headModel = baseModel.output
    # headModel = Flatten(name="flatten")(base)
    headModel = Dense(512, activation="relu")(headModel)
    headModel = Dropout(0.5)(headModel)
    headModel = Dense(1, activation="sigmoid")(headModel)
    model = Model(inputs=baseModel.input, outputs=headModel)

    # loop over all layers in the base model and freeze them so they will
    # *not* be updated during the training process
    for layer in baseModel.layers:
        layer.trainable = False



if __name__ == "__main__":
    main()
