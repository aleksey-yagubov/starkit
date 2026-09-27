/* Derived from starkit 0.0.3 (PyPI), Babaev Azer Kahraman Ogly.
 * Original equations and tick/radian conventions are retained. See LICENSE.md.
 */
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <math.h>

static int read_vector(PyObject *object, double *out, Py_ssize_t count)
{
    PyObject *seq = PySequence_Fast(object, "expected a numeric sequence");
    if (!seq) return 0;
    if (PySequence_Fast_GET_SIZE(seq) != count) {
        PyErr_Format(PyExc_ValueError, "expected %zd elements", count);
        Py_DECREF(seq);
        return 0;
    }
    for (Py_ssize_t i = 0; i < count; ++i) {
        out[i] = PyFloat_AsDouble(PySequence_Fast_GET_ITEM(seq, i));
        if (PyErr_Occurred()) { Py_DECREF(seq); return 0; }
        if (!isfinite(out[i])) {
            PyErr_SetString(PyExc_ValueError, "values must be finite");
            Py_DECREF(seq);
            return 0;
        }
    }
    Py_DECREF(seq);
    return 1;
}

static double residual(double angle, double yt, double zt,
                       double x, double y, double z,
                       double b5, double a10, double b10, double c10)
{
    double c = cos(angle), s = sin(angle);
    double u = y*c + z*s, v = z*c - y*s;
    return ((yt+b5)*c + zt*s - c10) * (u*u-v*v-x*x)
           - a10 - b10*u/sqrt(v*v+x*x);
}

static int minimum(const double *values)
{
    int best = -1;
    for (int i = 0; i < 11; ++i)
        if (isfinite(values[i]) && (best < 0 || fabs(values[i]) < fabs(values[best])))
            best = i;
    return best;
}

static int append_solution(PyObject *result, double a10, double a9,
                           double a8, double a7, double a6, double a5)
{
    PyObject *row = Py_BuildValue("[dddddd]", a10, a9, a8, a7, a6, a5);
    if (!row) return 0;
    int ok = PyList_Append(result, row) == 0;
    Py_DECREF(row);
    return ok;
}

static PyObject *alpha_calculation(PyObject *self, PyObject *args)
{
    (void)self;
    double xt, yt, zt, x, y, z, w, sizes[10], limits[6][2];
    PyObject *sizes_obj, *limits_obj;
    if (!PyArg_ParseTuple(args, "dddddddOO:alpha_calculation",
                         &xt, &yt, &zt, &x, &y, &z, &w, &sizes_obj, &limits_obj))
        return NULL;
    if (!isfinite(xt) || !isfinite(yt) || !isfinite(zt) || !isfinite(x)
        || !isfinite(y) || !isfinite(z) || !isfinite(w)) {
        PyErr_SetString(PyExc_ValueError, "pose values must be finite");
        return NULL;
    }
    if (!read_vector(sizes_obj, sizes, 10)) return NULL;
    if (sizes[4] <= 0 || sizes[5] <= 0) {
        PyErr_SetString(PyExc_ValueError, "a7 and a8 must be positive");
        return NULL;
    }
    PyObject *seq = PySequence_Fast(limits_obj, "expected six joint limit pairs");
    if (!seq) return NULL;
    if (PySequence_Fast_GET_SIZE(seq) != 6) {
        Py_DECREF(seq);
        PyErr_SetString(PyExc_ValueError, "expected six joint limit pairs");
        return NULL;
    }
    for (int i = 0; i < 6; ++i) {
        if (!read_vector(PySequence_Fast_GET_ITEM(seq, i), limits[i], 2)) {
            Py_DECREF(seq);
            return NULL;
        }
        if (limits[i][0] > limits[i][1]) {
            Py_DECREF(seq);
            PyErr_SetString(PyExc_ValueError, "joint minimum exceeds maximum");
            return NULL;
        }
    }
    Py_DECREF(seq);
    double norm = sqrt(x*x+y*y+z*z);
    if (!isfinite(norm) || norm == 0) {
        PyErr_SetString(PyExc_ValueError, "orientation must have a finite nonzero norm");
        return NULL;
    }
    x /= norm; y /= norm; z /= norm;
    double a5=sizes[0], b5=sizes[1], a6=sizes[3], a7=sizes[4], a8=sizes[5];
    double a9=sizes[6], a10=sizes[7], b10=sizes[8], c10=sizes[9];
    double cos5=cos(w), sin5=sin(w);
    double xtp=xt*cos5+(yt+a5)*sin5, ytp=(yt+a5)*cos5-xt*sin5;
    double xp=x*cos5+y*sin5, yp=y*cos5-x*sin5, zp=z;
    double low=limits[1][0]*0.00058909, high=limits[1][1]*0.00058909;
    if (!isfinite(high-low)) {
        PyErr_SetString(PyExc_ValueError, "joint search interval is too large");
        return NULL;
    }
    double step1=(high-low)/10, samples[11];
    int points[10], count=0;
    for (int i=0; i<11; ++i)
        samples[i]=residual(low+i*step1, ytp, zt, xp, yp, zp, b5, a10, b10, c10);
    for (int i=0; i<10; ++i)
        if (isfinite(samples[i]) && isfinite(samples[i+1]) &&
            ((samples[i]>0 && samples[i+1]<0) || (samples[i]<0 && samples[i+1]>0)))
            points[count++]=i;
    if (!count) {
        int k=minimum(samples);
        if (k >= 0) {
            if (k==0) points[count++]=0;
            else if (k==10) points[count++]=9;
            else points[count++]=fabs(samples[k-1])<fabs(samples[k+1]) ? k-1 : k;
        }
    }
    PyObject *result=PyList_New(0);
    if (!result) return NULL;
    int iterations=1;
    for (int j=0; j<count; ++j) {
        double lim1=low+points[j]*step1, lim2=lim1+step1, alpha6=0;
        int valid=0;
        /* Width shrinks tenfold. Bound iterations even for pathological inputs. */
        for (int refine=0; refine<320; ++refine) {
            double step=(lim2-lim1)/10;
            for (int i=0; i<11; ++i)
                samples[i]=residual(lim1+i*step, ytp, zt, xp, yp, zp, b5, a10, b10, c10);
            int k=minimum(samples);
            if (k<0) break;
            int k2=k==0 ? 1 : k==10 ? 9 : fabs(samples[k-1])<fabs(samples[k+1]) ? k-1 : k+1;
            alpha6=lim1+k*step;
            lim1+=(k>k2 ? k2 : k)*step;
            lim2=lim1+step;
            if (lim2-lim1<0.00025) { valid=1; break; }
            if (++iterations > limits[1][1]-limits[1][0]) { valid=1; break; }
        }
        if (!valid) continue;
        double tan6=tan(alpha6);
        double alpha10=atan((-yp-zp*tan6)/sqrt((zp-yp*tan6)*(zp-yp*tan6)+xp*xp*(1+tan6*tan6)));
        if (!(limits[5][0]<alpha10*1698 && alpha10*1698<limits[5][1])) continue;
        double cos6=cos(alpha6), sin6=sin(alpha6);
        double alpha987=atan(-xp/(zp*cos6-yp*sin6));
        double sin987=sin(alpha987), cos987=cos(alpha987);
        double K1=a6*sin987+xtp*cos987+(zt*cos6-(ytp+b5)*sin6)*sin987;
        double K2=a9+a6*cos987+(zt*cos6-(ytp+b5)*sin6)*cos987-xtp*sin987
            +b10/cos(alpha10)+((ytp+b5)*cos6+zt*sin6-c10)*tan(alpha10);
        double m=(K1*K1+K2*K2+a8*a8-a7*a7)/(2*a8);
        double disc=K1*K1*m*m-(K1*K1+K2*K2)*(m*m-K2*K2);
        if (!isfinite(disc) || disc<0 || K1*K1+K2*K2==0) continue;
        double t[2]={(-K1*m+sqrt(disc))/(K1*K1+K2*K2),
                     (-K1*m-sqrt(disc))/(K1*K1+K2*K2)};
        if (!(fabs(t[0])<=1 && fabs(t[1])<=1)) continue;
        for (int branch=0; branch<2; ++branch) {
            double alpha9=asin(t[branch]);
            /* Preserve upstream's branch correction, pending geometric validation. */
            double cosine=(K1+t[branch]+m)/(-K2);
            if (fabs(cosine)<=1) {
                double other=acos(cosine);
                if ((alpha9>0 && other>alpha9) || (alpha9<0 && other<alpha9)) alpha9=other;
            }
            double alpha8=atan2(-(K1+a8*sin(alpha9)), -(K2+a8*cos(alpha9)))-alpha9;
            double alpha7=alpha9+alpha8-alpha987;
            if (!isfinite(alpha7) || !isfinite(alpha8) || !isfinite(alpha9)) continue;
            if (alpha7*1698<limits[2][0] || alpha7*1698>limits[2][1] ||
                alpha8*1698<limits[3][0] || alpha8*1698>limits[3][1] ||
                alpha9*1698<limits[4][0] || alpha9*1698>limits[4][1]) continue;
            if (!append_solution(result, alpha10, alpha9, alpha8, alpha7, alpha6, w)) {
                Py_DECREF(result);
                return NULL;
            }
        }
    }
    return result;
}

static PyMethodDef methods[] = {
    {"alpha_calculation", alpha_calculation, METH_VARARGS,
     "alpha_calculation(xt, yt, zt, x, y, z, w, sizes, limAlpha) -> list of solutions"},
    {NULL, NULL, 0, NULL}
};
static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT, .m_name="starkit", .m_size=-1, .m_methods=methods
};
PyMODINIT_FUNC PyInit_starkit(void) { return PyModule_Create(&module); }
