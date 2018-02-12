from head_angle_w_mag import *


def run():
    startTime = 550000
    endTime = 800000

    gliderTimeCutData = prepareGliderGyroData(dev_glider, glider_neutral_acc_vector, glider_gyro_calibration_vector,
                                              startTime, endTime)
    headTimeCutData = prepareGliderGyroData(dev_head, head_neutral_acc_vector, head_gyro_calibration_vector,
                                            startTime, endTime)
    headMagData = prepare_magnetometer_data_orientated(dev_head, head_neutral_acc_vector, startTime, endTime)

    gliderInterpolatedData = interpolateDatas(gliderTimeCutData, headTimeCutData)
    headInterpolatedData = interpolateDatas(headTimeCutData, gliderTimeCutData)

    gliderAngleData = cumulateZAxisData(gliderInterpolatedData)
    headAngleData = cumulateZAxisData(headInterpolatedData)

    headRelativeAngle = getHeadRelativeAngle(headInterpolatedData, gliderInterpolatedData)

    plotAll(headAngleData, gliderAngleData, headRelativeAngle, headMagData)


if __name__ == "__main__":
    run()
