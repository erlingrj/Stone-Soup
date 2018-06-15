import datetime

import numpy as np

from stonesoup.models import LinearGaussian1D
from stonesoup.predictor import KalmanPredictor
from stonesoup.updater import KalmanUpdater
from stonesoup.types import GaussianState, Detection
from stonesoup.initiator import SinglePointInitiator


def test_spi():
    """Test SinglePointInitiator"""

    # Prior state information
    prior_state = GaussianState(
        np.array([[0], [0]]),
        np.array([[100, 0], [0, 1]]))

    # Define a measurement model
    measurement_model = LinearGaussian1D(2, [0], 1)

    # Define the Initiator
    initiator = SinglePointInitiator(
        prior_state,
        measurement_model)

    # Define 2 detections from which tracks are to be initiated
    timestamp = datetime.datetime.now()
    detections = [Detection(np.array([[4.5]]), timestamp),
                  Detection(np.array([[-4.5]]), timestamp)]

    # Run the initiator based on the available detections
    tracks = initiator.initiate(detections)

    # Ensure same number of tracks are initiated as number of measurements
    # (i.e. 2)
    assert(len(tracks) == 2)

    # Ensure that tracks are initiated correctly
    evaluated_tracks = [False, False]
    for detection in detections:

        detection_state_vec = detection.state_vector

        meas_pred_state_vec, meas_pred_covar, cross_covar =\
            KalmanPredictor._predict_meas(
                prior_state.state_vector,
                prior_state.covar,
                measurement_model.matrix(),
                measurement_model.covar())

        post_state_vec, post_state_covar, kalman_gain =\
            KalmanUpdater._update(prior_state.state_vector,
                                  prior_state.covar,
                                  detection_state_vec,
                                  meas_pred_state_vec,
                                  meas_pred_covar,
                                  cross_covar)

        eval_track_state = GaussianState(
            post_state_vec,
            post_state_covar,
            timestamp=detection.timestamp)

        # Compare against both tracks
        for track_idx, track in enumerate(tracks):
            if(np.array_equal(eval_track_state.mean, track.mean)
               and np.array_equal(eval_track_state.covar, track.covar)):

                evaluated_tracks[track_idx] = True

    # Ensure both tracks have been evaluated
    assert(all(evaluated_tracks))