#include "Beeper.h"
#include "array_functions.h"

static PyMethodDef module_methods[] = {
    {"NonZeroSubArray", (PyCFunction)NonZeroSubArray, METH_O,
     "Return the non-zero subarray."},

    {NULL}  /* Sentinel */
};

#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
initCWtrainer(void) 
{
    PyObject* m;

    if (PyType_Ready(&BeeperType) < 0)
        return;

    m = Py_InitModule3("CWtrainer", module_methods,
                       "Example module that creates an extension type.");

    if (m == NULL)
      return;

    Py_INCREF(&BeeperType);
    PyModule_AddObject(m, "Beeper", (PyObject *)&BeeperType);

}
