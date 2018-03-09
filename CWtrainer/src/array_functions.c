#include "array_functions.h"

static
int nonzero_subarray(short **array, Py_ssize_t *length)
{
    short *end = *array + *length - 1; /*the last item inside*/

    /* find the first nonzero data */
    while(**array==0 && *length > 0){
	(*array)++;
	(*length)--;
    }

    /* find the last nonzero data */
    while(*end==0 && *length > 0){
	end--;
	(*length)--;
    }

    return 0;
}

PyObject *NonZeroSubArray(PyObject *self, PyObject *obj)
{
    if(!PyString_Check(obj)){
	PyErr_SetString(PyExc_TypeError,"Must be called with string argument");
	return NULL;
    }

    Py_ssize_t length = PyString_Size(obj) / sizeof(short);
    short *array = (short*)(((PyStringObject*)obj)->ob_sval);
    nonzero_subarray(&array,&length);

    return Py_BuildValue("s#", array, length*sizeof(short));
}
