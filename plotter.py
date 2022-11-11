def plotAccelerationWithPeaks(axes, acceleration,peaks):
    axes.plot(acceleration)
    axes.plot(acceleration[peaks].to_frame(),
            ".", markersize=20, picker=True)

    axes.grid(True, 'both')
    axes.set_xlabel("time [cs]")
    axes.set_ylabel("Acceleration [ms^2]")