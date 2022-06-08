# CREDIT : "https://gist.github.com/friedkeenan/3bfc23d02170e41448a2a6f8ec28ac85" (friedkeenan/epicycle.py) manim ce
# A little bit of change.
# It's not good code.
# In future i will update this.
# it's slow!!
# Better code : "https://github.com/FillahAlamsyah/Belajar-Manim/blob/main/fourier_epicycles.py" (FillahAlamsyah/Belajar-Manim) manim ce ?
# Better code is using Fast Fourier Transform


from manim import *
from svg.path import parse_path


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!?
def integrate(func, a, b, *, dx=0.01): #TODO : Numerical integrate
    return sum(func(x) * dx for x in np.arange(a, b, dx))
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!?


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!?
class SVGPath(VMobject): #TODO : Making OBJ that can encode svg path
                        #TODO : inheritance from Vmobject (Mean : OBJ can use method of class Vmobject)
    def __init__(self, path_str, *, num_points=500, **kwargs):
        self.path       = parse_path(path_str)
        self.num_points = num_points
        super().__init__(**kwargs)



    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def point(self, alpha):
        z = self.path.point(alpha)
        return np.array([z.real, z.imag, 0])
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    


    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def generate_points(self):
        step = 1 / self.num_points
        points = [self.point(x) for x in np.arange(0, 1, step)]
        self.start_new_path(points[0])
        self.add_points_as_corners(points[1:])
        self.add_line_to(self.point(1))

        self.flip(RIGHT)
        self.center()
 
        return self
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!?


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!?
class Epicycle(VMobject):
    def __init__(self, path, coeff_start, coeff_end=None, *, num_points=500, COORDINATE = ORIGIN, **kwargs):
        # ? DONE
        self.COORDINATE = COORDINATE
        self.num_points = num_points
        self.T_number = coeff_start
        if coeff_end is None:
            coeff_end   = int(np.ceil(coeff_start / 2))
            coeff_start = coeff_end - coeff_start

        self.coeffs = self.gen_fourier_coeffs(path, coeff_start, coeff_end) #TODO : Do This First
        super().__init__(**kwargs)




    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #  ? DONE
    def gen_fourier_coeffs(self, path, start, end): # TODO : IMPORTANCE : Generate Coeffs
        def point(alpha):
            pt = path.point_from_proportion(alpha) - path.get_center()
            return complex(pt[0], pt[1])
        #TODO : {speed_n: radius_n, ......} dict (speed_n -> radius_n)
        return {i: integrate(lambda x: point(x) * np.exp(x * -i * TAU * 1j), 0, 1) for i in range(start, end)}
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!




    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # ? DONE
    def generate_points(self):
        step = 1 / self.num_points
        points = [self.point(x) for x in np.arange(0, 1, step)]
        self.start_new_path(points[0])
        self.add_points_as_corners(points[1:])
        self.add_line_to(points[0])

        return self
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!




    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # ? DONE alpha in range 0 to 1
    def point(self, alpha):
        #TODO : coeffs ==> Maybe {-1 : 1.2345, 0 : 1.2345, 1 : 1.2345} == {n : C_n, .....}
        #TODO : C_n == radius (scaling vector) ,,,  n == speed
        z = sum(C_n * np.exp(alpha * n * TAU * 1j) for n, C_n in self.coeffs.items())
        return np.array([z.real, z.imag, 0])
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!




    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def draw_circles(self, alpha, whole_mobject=None, **kwargs):
        if whole_mobject is None:
            whole_mobject = self.copy()

        self.submobjects.clear()
        self.pointwise_become_partial(whole_mobject, 0, alpha)

        speeds_and_radii = sorted(self.coeffs.items(), key=lambda x: abs(x[1]), reverse=True)

        z = 0
        tmp = self.COORDINATE
        C = 0
        prev_center_start_arrow = tmp
        for speed, radius in speeds_and_radii:
            C += 1
            self.T_number -= 1
            circ = Circle(**kwargs)
            circ.set_stroke(color = GREEN , opacity=0.6)
            circ.scale(abs(radius))
            tmp = np.array((z.real, z.imag, 0)) + self.COORDINATE
            circ.move_to(tmp)
            self.add(circ)
            if (self.T_number > 0):
                self.add(circ.set_stroke(opacity=0))
            if (C > 4):
                my_pointer = Line(prev_center_start_arrow, tmp, stroke_width = 0.5).add_tip(tip_length=0.03)
                self.add(my_pointer)
                if (self.T_number > 0):
                    self.add(my_pointer.set_opacity(0))
            prev_center_start_arrow = tmp
            z += radius * np.exp(alpha * speed * TAU * 1j)
        return self
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    def set_COORDINATE(self, COORDINATE1):
        self.COORDINATE = COORDINATE1



    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def animate_circles(self, **kwargs):
        class Draw(Animation):
            def interpolate_submobject(self, submobject, starting_submobject, alpha):
                submobject.draw_circles(alpha, starting_submobject, **kwargs)
        return Draw(self)
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!?


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!?
class EpicCycle(Scene):
    p_T = "M 0.09 0.486 L 0.09 0.242 L 0 0.242 L 0 0.164 L 0.092 0.164 L 0.111 0 L 0.18 0 L 0.18 0.164 L 0.324 0.164 L 0.324 0.242 L 0.18 0.242 L 0.18 0.493 A 0.216 0.216 0 0 0 0.182 0.521 Q 0.186 0.551 0.199 0.568 A 0.056 0.056 0 0 0 0.204 0.574 Q 0.229 0.597 0.263 0.597 Q 0.288 0.597 0.311 0.589 A 0.257 0.257 0 0 0 0.342 0.575 A 0.228 0.228 0 0 0 0.352 0.57 L 0.377 0.642 A 0.185 0.185 0 0 1 0.361 0.651 Q 0.353 0.654 0.343 0.658 A 0.434 0.434 0 0 1 0.323 0.665 Q 0.289 0.677 0.252 0.677 A 0.183 0.183 0 0 1 0.2 0.67 A 0.139 0.139 0 0 1 0.134 0.627 A 0.161 0.161 0 0 1 0.101 0.568 Q 0.094 0.544 0.091 0.515 A 0.348 0.348 0 0 1 0.09 0.486 Z"
    p_A1 = "M 0.391 0.054 L 0.391 0.012 L 0.473 0.012 L 0.473 0.406 A 0.121 0.121 0 0 0 0.474 0.422 Q 0.477 0.447 0.492 0.456 Q 0.51 0.467 0.532 0.467 L 0.513 0.537 Q 0.419 0.537 0.398 0.463 A 0.135 0.135 0 0 1 0.397 0.459 A 0.213 0.213 0 0 1 0.366 0.493 A 0.285 0.285 0 0 1 0.335 0.518 A 0.149 0.149 0 0 1 0.285 0.539 Q 0.265 0.543 0.241 0.544 A 0.272 0.272 0 0 1 0.234 0.544 Q 0.169 0.544 0.116 0.511 A 0.229 0.229 0 0 1 0.042 0.436 A 0.279 0.279 0 0 1 0.032 0.418 A 0.272 0.272 0 0 1 0.005 0.338 A 0.366 0.366 0 0 1 0 0.275 A 0.331 0.331 0 0 1 0.01 0.192 A 0.28 0.28 0 0 1 0.032 0.135 Q 0.063 0.073 0.119 0.037 A 0.223 0.223 0 0 1 0.23 0 A 0.274 0.274 0 0 1 0.246 0 A 0.226 0.226 0 0 1 0.294 0.005 A 0.187 0.187 0 0 1 0.328 0.016 A 0.26 0.26 0 0 1 0.37 0.038 A 0.221 0.221 0 0 1 0.391 0.054 Z M 0.383 0.399 L 0.383 0.12 Q 0.356 0.101 0.324 0.09 Q 0.291 0.078 0.255 0.078 A 0.159 0.159 0 0 0 0.205 0.086 A 0.14 0.14 0 0 0 0.171 0.103 Q 0.134 0.127 0.113 0.171 A 0.207 0.207 0 0 0 0.095 0.227 A 0.277 0.277 0 0 0 0.092 0.272 A 0.256 0.256 0 0 0 0.097 0.325 A 0.203 0.203 0 0 0 0.113 0.372 A 0.176 0.176 0 0 0 0.144 0.417 A 0.157 0.157 0 0 0 0.171 0.44 Q 0.208 0.464 0.254 0.464 Q 0.292 0.464 0.326 0.446 A 0.195 0.195 0 0 0 0.373 0.41 A 0.181 0.181 0 0 0 0.383 0.399 Z"
    p_N = "M 0.09 0.532 L 0 0.532 L 0 0.012 L 0.087 0.012 L 0.087 0.099 Q 0.115 0.057 0.159 0.029 A 0.173 0.173 0 0 1 0.23 0.002 A 0.226 0.226 0 0 1 0.262 0 Q 0.329 0 0.37 0.031 A 0.133 0.133 0 0 1 0.393 0.053 A 0.184 0.184 0 0 1 0.43 0.127 Q 0.436 0.153 0.437 0.184 A 0.338 0.338 0 0 1 0.437 0.193 L 0.437 0.532 L 0.347 0.532 L 0.347 0.203 A 0.193 0.193 0 0 0 0.344 0.166 Q 0.339 0.143 0.329 0.126 A 0.11 0.11 0 0 0 0.321 0.113 A 0.086 0.086 0 0 0 0.258 0.079 A 0.121 0.121 0 0 0 0.247 0.079 A 0.131 0.131 0 0 0 0.179 0.099 A 0.174 0.174 0 0 0 0.16 0.112 Q 0.119 0.144 0.09 0.188 L 0.09 0.532 Z"
    p_W = "M 0.263 0.525 L 0.164 0.525 L 0 0.029 L 0.083 0 L 0.217 0.423 L 0.339 0.042 L 0.436 0.042 L 0.555 0.423 L 0.688 0 L 0.768 0.029 L 0.603 0.525 L 0.504 0.525 L 0.384 0.138 L 0.263 0.525 Z"
    p_A2 = "M 0.391 0.054 L 0.391 0.012 L 0.473 0.012 L 0.473 0.406 A 0.121 0.121 0 0 0 0.474 0.422 Q 0.477 0.447 0.492 0.456 Q 0.51 0.467 0.532 0.467 L 0.513 0.537 Q 0.419 0.537 0.398 0.463 A 0.135 0.135 0 0 1 0.397 0.459 A 0.213 0.213 0 0 1 0.366 0.493 A 0.285 0.285 0 0 1 0.335 0.518 A 0.149 0.149 0 0 1 0.285 0.539 Q 0.265 0.543 0.241 0.544 A 0.272 0.272 0 0 1 0.234 0.544 Q 0.169 0.544 0.116 0.511 A 0.229 0.229 0 0 1 0.042 0.436 A 0.279 0.279 0 0 1 0.032 0.418 A 0.272 0.272 0 0 1 0.005 0.338 A 0.366 0.366 0 0 1 0 0.275 A 0.331 0.331 0 0 1 0.01 0.192 A 0.28 0.28 0 0 1 0.032 0.135 Q 0.063 0.073 0.119 0.037 A 0.223 0.223 0 0 1 0.23 0 A 0.274 0.274 0 0 1 0.246 0 A 0.226 0.226 0 0 1 0.294 0.005 A 0.187 0.187 0 0 1 0.328 0.016 A 0.26 0.26 0 0 1 0.37 0.038 A 0.221 0.221 0 0 1 0.391 0.054 Z M 0.383 0.399 L 0.383 0.12 Q 0.356 0.101 0.324 0.09 Q 0.291 0.078 0.255 0.078 A 0.159 0.159 0 0 0 0.205 0.086 A 0.14 0.14 0 0 0 0.171 0.103 Q 0.134 0.127 0.113 0.171 A 0.207 0.207 0 0 0 0.095 0.227 A 0.277 0.277 0 0 0 0.092 0.272 A 0.256 0.256 0 0 0 0.097 0.325 A 0.203 0.203 0 0 0 0.113 0.372 A 0.176 0.176 0 0 0 0.144 0.417 A 0.157 0.157 0 0 0 0.171 0.44 Q 0.208 0.464 0.254 0.464 Q 0.292 0.464 0.326 0.446 A 0.195 0.195 0 0 0 0.373 0.41 A 0.181 0.181 0 0 0 0.383 0.399 Z"

    def construct(self):
        num = 20

        P_0 = SVGPath(path_str = self.p_T, fill_color = (GREEN_A, GREEN_D), fill_opacity = 0.8).scale(1.2).move_to([-3.35846, 0., 0.])
        P_1 = SVGPath(path_str =self.p_A1, fill_color = (GREEN_A, GREEN_D), fill_opacity = 0.8).scale(1.2).move_to([-1.81375, 0., 0.])
        P_2 = SVGPath(path_str =self.p_N, fill_color = (GREEN_A, GREEN_D), fill_opacity = 0.8).scale(1.2).move_to([-0.23300, 0., 0.])
        P_3 = SVGPath(path_str =self.p_W, fill_color = (GREEN_A, GREEN_D), fill_opacity = 0.8).scale(1.2).move_to([1.48838, 0., 0.])
        P_4 = SVGPath(path_str =self.p_A2, fill_color = (GREEN_A, GREEN_D), fill_opacity = 0.8).scale(1.2).move_to([3.26609, 0., 0.])


        ep0 = Epicycle(P_0, coeff_start=num, COORDINATE=[-3.35846, 0., 0.]).move_to([-3.35846, 0., 0.])
        ep1 = Epicycle(P_1, coeff_start=num, COORDINATE=[-1.81375, 0., 0.]).move_to([-1.81375, 0., 0.])
        ep2 = Epicycle(P_2, coeff_start=num, COORDINATE=[-0.23300, 0., 0.]).move_to([-0.23300, 0., 0.])
        ep3 = Epicycle(P_3, coeff_start=num, COORDINATE=[1.48838, 0., 0.]).move_to([1.48838, 0., 0.])
        ep4 = Epicycle(P_4, coeff_start=num, COORDINATE=[3.26609, 0., 0.]).move_to([3.26609, 0., 0.])


        tag = Tex(f"coeff : {num} ; fourier series ; manim ce").to_corner(UL)
        self.play(Write(tag), run_time = 0.7)
        self.wait(0.7)
        self.play(
            ep0.animate_circles(),
            ep1.animate_circles(),
            ep2.animate_circles(),
            ep3.animate_circles(),
            ep4.animate_circles(),
            run_time = 2, rate_func = linear
        )
        self.wait(0.3)
        self.play(
            Uncreate(ep0),
            Uncreate(ep1),
            Uncreate(ep2),
            Uncreate(ep3),
            Uncreate(ep4),
            run_time = 0.7
        )
        big_obj = VGroup(P_0, P_1, P_2, P_3, P_4)
        self.play(
            Create(big_obj),
            run_time = 1
        )
        self.wait(0.6)
        self.play(Uncreate(big_obj), run_time = 0.5)
        self.wait(0.2)
