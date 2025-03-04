
def get_triangle_m_and_I(p0, p1, p2):
    cm = (p0 + p1 + p2) / 3

    v1 = p1 - p0
    v2 = p2 - p0

    r = abs(v1.dot(v2.rotated_270()))
    m = r / 2

    I_p0 = r * ((v1.abs_2() + v2.abs_2() + v1.dot(v2)) / 12)
    I = I_p0 - (p0 - cm).abs_2() * m

    return m, I

