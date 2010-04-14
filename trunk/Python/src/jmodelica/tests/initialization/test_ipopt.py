# -*- coding: utf-8 -*-
""" Tests the jmi wrappers for the IPOPT solver module. """
#    Copyright (C) 2009 Modelon AB
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os

import numpy as N
import ctypes as ct
from ctypes import byref
import nose.tools

import jmodelica
from jmodelica.tests import testattr
from jmodelica.compiler import OptimicaCompiler
from jmodelica import jmi
from jmodelica.initialization.ipopt import NLPInitialization
from jmodelica.initialization.ipopt import InitializationOptimizer

int = N.int32
N.int = N.int32

jm_home = jmodelica.environ['JMODELICA_HOME']
path_to_examples = os.path.join('Python','jmodelica','examples')
path_to_tests = os.path.join(jm_home, "Python", "jmodelica", "tests")

oc = OptimicaCompiler()

model = os.path.join('files','CSTR.mo')
fpath = os.path.join(jm_home, path_to_examples, model)
cpath = "CSTR.CSTR_Init"
fname = cpath.replace('.','_')
oc.compile_model(cpath, fpath, 'ipopt')

model_daeinit = os.path.join("files", "DAEInitTest.mo")
fpath_daeinit = os.path.join(path_to_tests, model_daeinit)
cpath_daeinit = "DAEInitTest"
fname_daeinit = cpath_daeinit.replace('.','_',1)
        
oc.set_boolean_option('state_start_values_fixed',True)
oc.compile_model(cpath_daeinit, fpath_daeinit, target='ipopt')

class TestNLPInitWrappers:
    """ Tests for NLPInitialization wrapper methods.
    
    """
    
    def setUp(self):
        """Test setUp. Load the test model."""        
        cstr = jmi.Model(fname)    
        self.init_nlp = NLPInitialization(cstr)     
     
    @testattr(stddist = True)   
    def test_init_opt_get_dimensions(self):
        """ Test NLPInitialization.init_opt_get_dimensions"""
        (nx,n_h,dh_n_nz) = self.init_nlp.init_opt_get_dimensions()

#    @testattr(stddist = True)
#    def test_init_opt_get_x(self):
#       """ Test NLPInitialization.init_opt_get_x"""
#       (nx,n_h,dh_n_nz) = self.init_nlp.init_opt_get_dimensions()
#       x=self.init_nlp.init_opt_get_x()
#       nose.tools.assert_equal(len(x),nx)
    
    @testattr(stddist = True)  
    def test_init_opt_getset_initial(self):
        """ Test NLPInitialization.init_opt_get_initial"""
        (nx,n_h,dh_n_nz)=self.init_nlp.init_opt_get_dimensions()
        x_init=N.zeros(nx)
        self.init_nlp.init_opt_get_initial(x_init)
        self.init_nlp.init_opt_set_initial(x_init)
    
    @testattr(stddist = True)           
    def test_init_opt_getset_bounds(self):
        """ Test NLPInitialization.init_opt_get_bounds and init_opt_set_bounds"""
        (nx,n_h,dh_n_nz)=self.init_nlp.init_opt_get_dimensions()
        x_lb=N.zeros(nx)
        x_ub=N.zeros(nx)
        self.init_nlp.init_opt_get_bounds(x_lb,x_ub)
        self.init_nlp.init_opt_set_bounds(x_lb,x_ub)       
        
    @testattr(stddist = True)    
    def test_init_opt_f(self):
        """ Test NLPInitialization.init_opt_f"""
        f=N.zeros(1)
        self.init_nlp.init_opt_f(f)
    
    @testattr(stddist = True)   
    def test_init_opt_df(self):
        """ Test NLPInitialization.init_opt_df"""
        (nx,n_h,dh_n_nz)=self.init_nlp.init_opt_get_dimensions()
        df=N.zeros(nx)
        self.init_nlp.init_opt_df(df)

    @testattr(stddist = True)   
    def test_init_opt_h(self):
        """ Test NLPInitialization.opt_sim_h"""
        (nx,n_h,dh_n_nz)=self.init_nlp.init_opt_get_dimensions()
        res=N.zeros(n_h)
        self.init_nlp.init_opt_h(res)
    
    @testattr(stddist = True)   
    def test_init_opt_dh(self):
        """ Test NLPInitialization.opt_sim_dh"""
        (nx,n_h,dh_n_nz)=self.init_nlp.init_opt_get_dimensions()
        jac=N.zeros(dh_n_nz)
        self.init_nlp.init_opt_dh(jac)
    
    @testattr(stddist = True)    
    def test_opt_init_opt_dh_nz_indices(self):
        """ Test NLPInitialization.opt_sim_dh_nz_indices"""
        (nx,n_h,dh_n_nz)=self.init_nlp.init_opt_get_dimensions()
        irow=N.zeros(dh_n_nz,dtype=int)
        icol=N.zeros(dh_n_nz,dtype=int)
        self.init_nlp.init_opt_dh_nz_indices(irow,icol)


class TestNLPInit:
    """ Test evaluation of function in NLPInitialization and solution
    of initialization problems.
    
    """
    
    def setUp(self):
        """Test setUp. Load the test model."""                    
        # Load the dynamic library and XML data
        self.dae_init_test = jmi.Model(fname_daeinit)

        # This is to check that values set in the model prior to
        # creation of the NLPInitialization object are used as an
        # initial guess.
        self.dae_init_test.set_value('y1',0.3)
    
        self.init_nlp = NLPInitialization(self.dae_init_test)

    @testattr(stddist = True)    
    def test_init_opt_get_dimensions(self):
        """ Test NLPInitialization.init_opt_get_dimensions"""
    
        res_n_x = 8
        res_n_h = 8
        res_dh_n_nz = 17
    
        n_x, n_h, dh_n_nz = self.init_nlp.init_opt_get_dimensions()
    
        assert N.abs(res_n_x-n_x) + N.abs(res_n_h-n_h) + \
               N.abs(res_dh_n_nz-dh_n_nz)==0, \
               "test_jmi.py: test_init_opt: init_opt_get_dimensions returns wrong problem dimensions." 

    @testattr(stddist = True)    
    def test_init_opt_get_set_x_init(self):

        n_x, n_h, dh_n_nz = self.init_nlp.init_opt_get_dimensions()
    
        # Test init_opt_get_x_init
        res_x_init = N.array([0,0,3,4,1,0,0,0])
        x_init = N.zeros(n_x)
        self.init_nlp.init_opt_get_initial(x_init)
        #print x_init
        assert N.sum(N.abs(res_x_init-x_init))<1e-3, \
               "test_jmi.py: test_init_opt: init_opt_get_x_init returns wrong values." 
    
        # Test init_opt_set_x_init
        res_x_init = N.ones(n_x)
        x_init = N.ones(n_x)
        self.init_nlp.init_opt_set_initial(x_init)
        self.init_nlp.init_opt_get_initial(x_init)
        assert N.sum(N.abs(res_x_init-x_init))<1e-3, \
               "test_jmi.py: test_init_opt: init_opt_get_x_init returns wrong values after setting the initial values with init_opt_get_x_init." 

    @testattr(stddist = True)    
    def test_init_opt_get_set_bounds(self):

        n_x, n_h, dh_n_nz = self.init_nlp.init_opt_get_dimensions()

        # Test init_opt_get_bounds
        res_x_lb = -1e20*N.ones(n_x)
        res_x_ub = 1e20*N.ones(n_x)
        x_lb = N.zeros(n_x)
        x_ub = N.zeros(n_x)
        self.init_nlp.init_opt_get_bounds(x_lb,x_ub)
        assert N.sum(N.abs(res_x_lb-x_lb))<1e-3, \
               "test_jmi.py: test_init_opt: init_opt_get_bounds returns wrong lower bounds." 
        assert N.sum(N.abs(res_x_lb-x_lb))<1e-3, \
               "test_jmi.py: test_init_opt: init_opt_get_bounds returns wrong upper bounds." 
    
        # Test init_opt_set_bounds
        res_x_lb = -5000*N.ones(n_x)
        res_x_ub = 5000*N.ones(n_x)
        x_lb = -5000*N.ones(n_x)
        x_ub = 5000*N.ones(n_x)
        self.init_nlp.init_opt_set_bounds(x_lb,x_ub)
        self.init_nlp.init_opt_get_bounds(x_lb,x_ub)
        assert N.sum(N.abs(res_x_lb-x_lb))<1e-3, \
               "test_jmi.py: test_init_opt: init_opt_get_bounds returns wrong lower bounds after calling init_opt_set_bounds." 
        assert N.sum(N.abs(res_x_lb-x_lb))<1e-3, \
               "test_jmi.py: test_init_opt: init_opt_get_bounds returns wrong upper bounds after calling init_opt_set_bounds." 

    @testattr(stddist = True)    
    def test_init_opt_f(self):

        n_x, n_h, dh_n_nz = self.init_nlp.init_opt_get_dimensions()
    
        # Test init_opt_f
        res_f = N.array([0.0])
        f = N.zeros(1)
        self.init_nlp.init_opt_f(f)
        #print f
        assert N.sum(N.abs(res_f-f))<1e-3, \
               "test_jmi.py: test_init_opt: init_opt_f returns wrong value" 

    @testattr(stddist = True)    
    def test_init_opt_df(self):

        n_x, n_h, dh_n_nz = self.init_nlp.init_opt_get_dimensions()

        # Test init_opt_df
        res_df = N.array([0.,0,0,0,0,0,0,0])
        df = N.ones(n_x)
        self.init_nlp.init_opt_df(df)
        #print df
        assert N.sum(N.abs(res_df-df))<1e-3, \
               "test_jmi.py: test_init_opt: init_opt_df returns wrong value" 

    @testattr(stddist = True)    
    def test_init_opt_h(self):

        n_x, n_h, dh_n_nz = self.init_nlp.init_opt_get_dimensions()
        # Test init_opt_h
        res_h = N.array([ -1.98158529e+02,  -2.43197505e-01,   5.12000000e+02,   5.00000000e+00,
                          1.41120008e-01,   0.00000000e+00,   0.00000000e+00,   0.00000000e+00])
        h = N.zeros(n_h)
        self.init_nlp.init_opt_h(h)
        #print h
        assert N.sum(N.abs(res_h-h))<1e-3, \
               "test_jmi.py: test_init_opt: init_opt_h returns wrong value" 

    @testattr(stddist = True)    
    def test_init_opt_dh(self):
        n_x, n_h, dh_n_nz = self.init_nlp.init_opt_get_dimensions()

        # Test init_opt_dh
        res_dh = N.array([ -1.,           -1.,         -135.,          192.,           -0.9899925,    -1.,
                           -48.,            0.65364362,   -1.,            0.54030231,   -2.,           -1.,
                           -1.,            0.9899925,   192.,           -1.,           -1.,        ])
        dh = N.ones(dh_n_nz)
        self.init_nlp.init_opt_dh(dh)
        #print dh
        assert N.sum(N.abs(res_dh-dh))<1e-3, \
               "test_jmi.py: test_init_opt: init_opt_dh returns wrong value" 

    @testattr(stddist = True)    
    def test_init_opt_dh_nz_indices(self):

        n_x, n_h, dh_n_nz = self.init_nlp.init_opt_get_dimensions()

        # Test init_opt_dh_nz_indices
        res_dh_irow = N.array([1, 2, 1, 3, 5, 7, 1, 2, 8, 1, 2, 6, 3, 5, 3, 4, 5])
        res_dh_icol = N.array([1, 2, 3, 3, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 7, 7, 8])
        dh_irow = N.zeros(dh_n_nz,dtype=N.int32)
        dh_icol = N.zeros(dh_n_nz,dtype=N.int32)
        self.init_nlp.init_opt_dh_nz_indices(dh_irow,dh_icol)
        assert N.sum(N.abs(res_dh_irow-dh_irow))<1e-3, \
               "test_jmi.py: test_init_opt: init_opt_dh_nz_indices returns wrong values for the row indices." 
        assert N.sum(N.abs(res_dh_icol-dh_icol))<1e-3, \
               "test_jmi.py: test_init_opt: init_opt_dh_nz_indices returns wrong values for the column indices" 

    @testattr(stddist = True)    
    def test_init_opt_solve(self):

        n_x, n_h, dh_n_nz = self.init_nlp.init_opt_get_dimensions()

        # Test optimization of initialization system
        self.init_nlp_ipopt = InitializationOptimizer(self.init_nlp)
    
        # self.init_nlp_ipopt.init_opt_ipopt_set_string_option("derivative_test","first-order")
        
        self.init_nlp_ipopt.init_opt_ipopt_solve()
    
        res_Z = N.array([5.,
                         -198.1585290151921,
                         -0.2431975046920718,
                         3.0,
                         4.0,
                         1.0,
                         2197.0,
                         5.0,
                         -0.92009689684513785,
                         0.])
    
        assert max(N.abs(res_Z-self.dae_init_test.get_z()))<1e-3, \
               "test_jmi.py: test_init_opt: Wrong solution to initialization system." 
        

        
