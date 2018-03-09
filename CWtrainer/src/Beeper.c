#include "Beeper.h"
#include <stdbool.h>
#include <math.h>

typedef struct {
    PyObject_HEAD
    /*initiated by user*/
    double frequency_Hz; 
    double bandwidth_Hz;
    double volume_pct;
    double samprate_Hz;
    
    /*derived constants*/
    double period_s; /*derived from frequency*/
    double ramp_period; /*derived from bandwidth*/
    double tick_s; /*the time spent on one sample*/
    double omega_Hz; /*the angular frequency*/

    /*internal use*/
    double time_mod_period_s; /*to keep phase*/
    double curr_amp;

} Beeper;

/******************************************************************/
/* caclulate the next frame based on a bunch of object properties */
/* such as: - the current time                                    */
/*          - the frequency                                       */
/*          - the current amplitude                               */
/* and increment the necessary items at the same time.            */
/******************************************************************/
static short Beeper_NextFrame(Beeper *self)
{
    short result = 0;

    result = SHRT_MAX * self->curr_amp * sin( self->omega_Hz * self->time_mod_period_s);

    self->time_mod_period_s += self->tick_s;


    if (self->time_mod_period_s > self->period_s)
	self->time_mod_period_s -= self->period_s;

    return result;
}


/*============================================================*/
/*============================================================*/
/*============================================================*/
/*                 Python methods                             */
/*============================================================*/
/*============================================================*/
/*============================================================*/
static PyObject *
Beeper_params(Beeper* self)
{
    PyObject *result;
    
    result = Py_BuildValue("{s:d,s:d,s:d,s:d}", 
			   "frequency",self->frequency_Hz,
			   "bandwidth",self->bandwidth_Hz,
			   "volume",self->volume_pct,
			   "samprate",self->samprate_Hz);
    if (result == NULL)
        return NULL;
    
    return result;
}

static bool
Beeper_beep_level (Beeper *self, double level, short **start, Py_ssize_t nsamples)
{
    double target_amp = level * self->volume_pct;
    double old_amp = self->curr_amp;

    short *end = (*start)+nsamples;

    double ramp_time = 0.;
    double ramp_frac = 0.;

    if(target_amp != self->curr_amp){
	/* we need to ramp first */
	while(ramp_time < self->ramp_period){
	    ramp_time += self->tick_s;
	    
	    ramp_frac = (1. - cos(M_PI  * self->bandwidth_Hz * ramp_time) ) / 2.;
	    /* the following will ramp the amplitude  */
            /* from one level to the other */
	    self->curr_amp = target_amp * ramp_frac + old_amp * (1-ramp_frac); 

	    **start = Beeper_NextFrame(self);
	    (*start)++;
	    if(*start==end)
		break;
	}

	if(ramp_time > self->ramp_period)
	    self->curr_amp = target_amp; /* make sure we got there if we got the time*/
    }
    /* ramping is done */
    /* now we will economize a bit if the actual amplitude is zero */
    
    /* printf("self->curr_amp %f\n",self->curr_amp); */
    
    if(self->curr_amp == 0.)
        for(; *start!=end; (*start)++)
	    **start = (short)0.;
	    /* we don't even keep track of time here. */
	    /* No-one cares about the phase in a period of silence */
    else
	for(; *start!=end; (*start)++)
	    **start = Beeper_NextFrame(self);
    
    /* return if there was an error */
    return false;
}

static PyObject *
Beeper_beep_sequence(Beeper* self,PyObject *obj)
{
    PyObject *seq=NULL, *period_tuple=NULL, *result=NULL;
    Py_ssize_t n_periods=0, i_period;


    bool error=false;

    seq = PySequence_Fast(obj, "expected a sequence");
    if(seq==NULL)
	return NULL;
    n_periods = PySequence_Size(seq);
    
/* convert the list of durations into a list of sample_durations and levels*/
    long sample_durations[n_periods];
    double levels[n_periods];
    double level, duration;
    
    for (i_period=0; i_period < n_periods; i_period++){
	period_tuple = PySequence_Fast_GET_ITEM(seq, i_period);
	/* each item should be a pair of duration,level */
	if(!PyArg_ParseTuple(period_tuple, "dd", &duration, &level)){
	    error = true;
	    break;
	}
	/* the duration and level are good. save them */
	sample_durations[i_period] = self->samprate_Hz * duration;
	levels[i_period] = level;
	/* printf("period saved level %f duration %f\n",level, duration); */
    }

    Py_DECREF(seq);    /* we are done with the sequence */

/* get the total duration of the sound */

    Py_ssize_t n_samples =0;
    for (i_period=0; i_period < n_periods; i_period++)
	n_samples += sample_durations[i_period];

/* allocate an array of shorts to handle this duration */
    
    short samples[n_samples];
    
/* for each sample duration, call a beep_level method on the array */
    
    short *next_start=samples;
    for (i_period=0; i_period < n_periods; i_period++){
	error = Beeper_beep_level(self,
				  levels[i_period],
				  &next_start,
				  sample_durations[i_period]);
	if(error) break;
    }
    
    
    if(!error) 
	result = Py_BuildValue("s#",samples,n_samples*sizeof(short));

    return result;
}

/*============================================================*/
/*============================================================*/
/*============================================================*/
/*                 Python boilerplate                         */
/*============================================================*/
/*============================================================*/
/*============================================================*/

static PyMethodDef Beeper_methods[] = {
    {"params", (PyCFunction)Beeper_params, METH_NOARGS,
	 "Return the parameters that the Beeper uses"
	 },
    {"beep_sequence", (PyCFunction)Beeper_beep_sequence, METH_O,
	 "Return the bytes to be written to the output"
	 },

    {NULL}  /* Sentinel */
};


static void
Beeper_dealloc(Beeper* self)
{
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
Beeper_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    Beeper *self;
    
    self = (Beeper *)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->frequency_Hz = 800.;
        self->bandwidth_Hz = 100.;
	self->volume_pct = 1.;
        self->samprate_Hz = 22050.; /* espeak outputs this */
    }

    return (PyObject *)self;
}

static int
Beeper_init(Beeper *self, PyObject *args, PyObject *kwds)
{

    static char *kwlist[] = {"frequency", "bandwidth", "volume", "samprate",NULL};

    if (! PyArg_ParseTupleAndKeywords(args, kwds, "|dddd", kwlist, 
                                      &self->frequency_Hz,
                                      &self->bandwidth_Hz,
                                      &self->volume_pct,
                                      &self->samprate_Hz))
        return -1; 
    
    /*derived values*/
    self->period_s = 1./self->frequency_Hz;
    self->tick_s = 1./self->samprate_Hz;
    self->ramp_period = 1./self->bandwidth_Hz;
    self->omega_Hz = 2. * M_PI * self->frequency_Hz;
    
    /*internal values*/
    self->time_mod_period_s = 0.;
    self->curr_amp = 0.;
    return 0;
}


static PyMemberDef Beeper_members[] = {
    /*no members*/

    {NULL}  /* Sentinel */
};

PyTypeObject BeeperType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "CWtrainer.Beeper",             /*tp_name*/
    sizeof(Beeper),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)Beeper_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "Beeper objects",           /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    Beeper_methods,             /* tp_methods */
    Beeper_members,             /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)Beeper_init,      /* tp_init */
    0,                         /* tp_alloc */
    Beeper_new,                 /* tp_new */
};

