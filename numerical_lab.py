"""Two constructed-model checks; Python standard library only.

Run: python numerical_lab.py
No files, network calls, or packages are required. Inputs are SI quantities.
"""

import math


def positive(name, value):
    """Reject nonfinite or nonpositive physical scales."""
    if not math.isfinite(value) or value <= 0:
        raise ValueError(name + " must be finite and positive")


def intervals(n):
    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise ValueError("N must be a positive integer")


def mass_study(n, reverse_x=False, kappa=0.2, rho0=1.0,
               duration=1.0, lengths=(0.5, 0.3, 0.2)):
    """Return mean storage, trapezoid efflux, normalized balance error.

    The six face integrals are exact in space. Only time is discretized.
    reverse_x deliberately reverses the outward normal on the x=Lx face.
    """
    intervals(n)
    for name, value in (("kappa", kappa), ("rho0", rho0),
                        ("duration", duration)):
        positive(name, value)
    if len(lengths) != 3:
        raise ValueError("three box lengths are required")
    for value in lengths:
        positive("box length", value)
    lx, ly, lz = lengths
    volume = lx * ly * lz
    storage = rho0 * volume * math.expm1(-2 * kappa * duration)
    storage /= duration

    def efflux(t):
        density = rho0 * math.exp(-2 * kappa * t)
        # Each entry is rho * (velocity dot outward normal) * face area.
        faces = (0.0, density * kappa * lx * ly * lz,
                 0.0, density * kappa * ly * lx * lz, 0.0, 0.0)
        if reverse_x:
            faces = (faces[0], -faces[1], *faces[2:])
        return math.fsum(faces)

    dt = duration / n
    total = 0.5 * (efflux(0.0) + efflux(duration))
    total += math.fsum(efflux(j * dt) for j in range(1, n))
    mean_efflux = total * dt / duration
    error = abs(storage + mean_efflux) / abs(storage)
    return storage, mean_efflux, error


def pipe_study(n, reverse_pressure=False, density=1000.0,
               viscosity=0.001, radius=0.001, length=0.2,
               gradient=100.0):
    """Return midpoint Q, signed wall force, normalized force residual.

    z is downstream, gradient=-dp/dz>0, axial body force is zero.
    Wall traction uses a backward difference at the stationary wall.
    """
    intervals(n)
    for name, value in (("density", density), ("viscosity", viscosity),
                        ("radius", radius), ("length", length),
                        ("gradient", gradient)):
        positive(name, value)
    dr = radius / n

    def velocity(r):
        return gradient * (radius * radius - r * r) / (4 * viscosity)

    flow = math.fsum(2 * math.pi * ((j + 0.5) * dr)
                     * velocity((j + 0.5) * dr) * dr for j in range(n))
    derivative = (velocity(radius) - velocity(radius - dr)) / dr
    wall_force = 2 * math.pi * radius * length * viscosity * derivative
    pressure_force = gradient * length * math.pi * radius ** 2
    if reverse_pressure:
        pressure_force = -pressure_force
    residual = abs(pressure_force + wall_force) / abs(pressure_force)
    return flow, wall_force, residual


def require_below(value, tolerance):
    """A balance acceptance check used by the deliberate failure probes."""
    if not math.isfinite(value) or value > tolerance:
        raise ValueError("balance residual exceeds tolerance")


def run_checks():
    ns = (4, 8, 16, 32, 64)
    mass = [mass_study(n) for n in ns]
    pipe = [pipe_study(n) for n in ns]
    exact_flow = math.pi * 100.0 * 0.001 ** 4 / (8 * 0.001)
    pressure_force = 100.0 * 0.2 * math.pi * 0.001 ** 2
    flow_errors = [abs(row[0] / exact_flow - 1) for row in pipe]
    for j, n in enumerate(ns):
        assert math.isclose(flow_errors[j], 1 / (2 * n * n),
                            rel_tol=1e-9)
        assert math.isclose(pipe[j][2], 1 / (2 * n), rel_tol=1e-10)
    for j in range(1, len(ns)):
        assert 3.99 < mass[j - 1][2] / mass[j][2] < 4.01
        assert math.isclose(flow_errors[j - 1] / flow_errors[j], 4.0,
                            rel_tol=1e-9)
        assert math.isclose(pipe[j - 1][2] / pipe[j][2], 2.0,
                            rel_tol=1e-10)
    require_below(mass[-1][2], 1e-5)
    require_below(pipe[-1][2], 0.01)
    for n in ns:
        assert math.isclose(mass_study(n, reverse_x=True)[2], 1.0)
        assert math.isclose(pipe_study(n, reverse_pressure=True)[2],
                            2 - 1 / (2 * n))
    for bad in (0, -1, 2.5, True):
        for study in (mass_study, pipe_study):
            try:
                study(bad)
            except ValueError:
                pass
            else:
                raise AssertionError("invalid N accepted")
    for study, kwargs in ((mass_study, {"duration": 0}),
                          (pipe_study, {"viscosity": -1}),
                          (pipe_study, {"radius": math.nan})):
        try:
            study(4, **kwargs)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid physical scale accepted")
    for residual in (mass_study(64, reverse_x=True)[2],
                     pipe_study(64, reverse_pressure=True)[2]):
        try:
            require_below(residual, 0.01)
        except ValueError:
            pass
        else:
            raise AssertionError("sign mutation was not rejected")
    return ns, mass, pipe, exact_flow, pressure_force, flow_errors


def main():
    ns, mass, pipe, exact_flow, force, flow_errors = run_checks()
    print("Constructed models; SI units; standard library only")
    print("MASS: mean storage [kg/s] = {:.9e}".format(mass[0][0]))
    print("N mean_efflux[kg/s] balance_error ratio")
    for j, n in enumerate(ns):
        ratio = "-" if j == 0 else "{:.6f}".format(
            mass[j - 1][2] / mass[j][2])
        print(f"{n:2d} {mass[j][1]:.9e} {mass[j][2]:.9e} {ratio}")
    print("PIPE: exact Q [m3/s] = {:.9e}".format(exact_flow))
    mean_speed = exact_flow / (math.pi * 0.001 ** 2)
    reynolds = 1000.0 * mean_speed * (2 * 0.001) / 0.001
    print("pressure force [N] = {:.9e}; Re_D = {:.6f}".format(
        force, reynolds))
    print("N Q_mid[m3/s] Q_rel_error wall_force[N] force_error")
    for j, n in enumerate(ns):
        print(f"{n:2d} {pipe[j][0]:.9e} {flow_errors[j]:.9e} "
              f"{pipe[j][1]:.9e} {pipe[j][2]:.9e}")
    print("MUTATIONS at N=64: reversed x-face error = {:.9e}".format(
        mass_study(64, reverse_x=True)[2]))
    print("reversed pressure error = {:.9e}".format(
        pipe_study(64, reverse_pressure=True)[2]))
    print("PASS: convergence, exact error identities, sign rejection, inputs")


if __name__ == "__main__":
    main()
