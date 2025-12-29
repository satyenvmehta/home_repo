
from base_lib.core.common_include import *
from base_lib.core.base_classes import *

from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class MLModel(ABC):
    """
    Base class for machine learning models.
    """
    # data: object  # Data for training the model (can be pandas.DataFrame or other)
    # target: str  # Name of the target variable in the data
    dirName : BaseString
    fileName : BaseString

    @abstractmethod
    def pre_process_data(self):
        """
        Performs data pre-processing steps.

        This function should be implemented in child classes to handle specific
        data pre-processing requirements for different model types.
        """
        pass

    @abstractmethod
    def train_model(self):
        """
        Trains the machine learning model.

        This function should be implemented in child classes to import and use
        the chosen machine learning library (e.g., scikit-learn, TensorFlow) to
        train the model on the pre-processed data.
        """
        pass

    def predict(self, new_data):
        """
        Makes predictions using the trained model.

        Args:
            new_data (object): The data on which to make predictions. (can be pandas.DataFrame or other)

        Returns:
            object: The predicted target values for the new data.
        """
        # Ensure the model is trained before making predictions
        if not hasattr(self, "_model"):
            print("Model is not trained yet. Please train the model first.")
            return None

        # Make predictions using the trained model
        predictions = self._model.predict(new_data)
        return predictions

    @abstractmethod
    def evaluate(self, test_data, test_target):
        """
        Evaluates the performance of the trained model on unseen data.

        This function should be implemented in child classes to choose
        appropriate evaluation metrics based on the model type and problem
        (e.g., accuracy, R-squared, etc.).

        Args:
            test_data (object): The testing data to evaluate the model on. (can be pandas.DataFrame or other)
            test_target (str): The name of the target variable in the testing data.
        """
        pass