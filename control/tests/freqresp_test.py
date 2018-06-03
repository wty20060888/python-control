#!/usr/bin/env python
#
# freqresp_test.py - test frequency response functions
# RMM, 30 May 2016 (based on timeresp_test.py)
#
# This is a rudimentary set of tests for frequency response functions,
# including bode plots.

import unittest
import numpy as np
import control as ctrl
from control.statesp import StateSpace
from control.matlab import ss, tf, bode
from control.exception import slycot_check
from control.tests.margin_test import assert_array_almost_equal
import matplotlib.pyplot as plt

class TestFreqresp(unittest.TestCase):
   def setUp(self):
      self.A = np.matrix('1,1;0,1')
      self.C = np.matrix('1,0')
      self.omega = np.linspace(10e-2,10e2,1000)

   def test_siso(self):
      B = np.matrix('0;1')
      D = 0
      sys = StateSpace(self.A,B,self.C,D)

      # test frequency response
      frq=sys.freqresp(self.omega)

      # test bode plot
      bode(sys)

      # Convert to transfer function and test bode
      systf = tf(sys)
      bode(systf)

   def test_superimpose(self):
      # Test to make sure that multiple calls to plots superimpose their
      # data on the same axes unless told to do otherwise

      # Generate two plots in a row; should be on the same axes
      plt.figure(1); plt.clf()
      ctrl.bode_plot(ctrl.tf([1], [1,2,1]))
      ctrl.bode_plot(ctrl.tf([5], [1, 1]))

      # Check to make sure there are two axes and that each axes has two lines
      assert len(plt.gcf().axes) == 2
      for ax in plt.gcf().axes:
         # Make sure there are 2 lines in each subplot
         assert len(ax.get_lines()) == 2
      
      # Generate two plots as a list; should be on the same axes
      plt.figure(2); plt.clf();
      ctrl.bode_plot([ctrl.tf([1], [1,2,1]), ctrl.tf([5], [1, 1])])

      # Check to make sure there are two axes and that each axes has two lines
      assert len(plt.gcf().axes) == 2
      for ax in plt.gcf().axes:
         # Make sure there are 2 lines in each subplot
         assert len(ax.get_lines()) == 2

      # Generate two separate plots; only the second should appear
      plt.figure(3); plt.clf();
      ctrl.bode_plot(ctrl.tf([1], [1,2,1]))
      plt.clf()
      ctrl.bode_plot(ctrl.tf([5], [1, 1]))

      # Check to make sure there are two axes and that each axes has one line
      assert len(plt.gcf().axes) == 2
      for ax in plt.gcf().axes:
         # Make sure there is only 1 line in the subplot
         assert len(ax.get_lines()) == 1

      # Now add a line to the magnitude plot and make sure if is there
      for ax in plt.gcf().axes:
         if ax.get_label() == 'control-bode-magnitude':
            break
      ax.semilogx([1e-2, 1e1], 20 * np.log10([1, 1]), 'k-')
      assert len(ax.get_lines()) == 2

   def test_doubleint(self):
      # 30 May 2016, RMM: added to replicate typecast bug in freqresp.py
      A = np.matrix('0, 1; 0, 0');
      B = np.matrix('0; 1');
      C = np.matrix('1, 0');
      D = 0;
      sys = ss(A, B, C, D);
      bode(sys);

   @unittest.skipIf(not slycot_check(), "slycot not installed")
   def test_mimo(self):
      # MIMO
      B = np.matrix('1,0;0,1')
      D = np.matrix('0,0')
      sysMIMO = ss(self.A,B,self.C,D)

      frqMIMO = sysMIMO.freqresp(self.omega)
      tfMIMO = tf(sysMIMO)

      #bode(sysMIMO) # - should throw not implemented exception
      #bode(tfMIMO) # - should throw not implemented exception

      #plt.figure(3)
      #plt.semilogx(self.omega,20*np.log10(np.squeeze(frq[0])))

      #plt.figure(4)
      #bode(sysMIMO,self.omega)

   def test_bode_margin(self):
      num = [1000]
      den = [1, 25, 100, 0]
      sys = ctrl.tf(num, den)
      ctrl.bode_plot(sys, margins=True,dB=False,deg = True, Hz=False)
      fig = plt.gcf()
      allaxes = fig.get_axes()

      mag_to_infinity = (np.array([6.07828691, 6.07828691]),
                         np.array([1.00000000e+00, 1.00000000e-08]))
      assert_array_almost_equal(mag_to_infinity, allaxes[0].lines[2].get_data())

      gm_to_infinty = (np.array([10., 10.]), np.array([4.00000000e-01, 1.00000000e-08]))
      assert_array_almost_equal(gm_to_infinty, allaxes[0].lines[3].get_data())

      one_to_gm = (np.array([10., 10.]), np.array([1., 0.4]))
      assert_array_almost_equal(one_to_gm, allaxes[0].lines[4].get_data())

      pm_to_infinity = (np.array([6.07828691, 6.07828691]),
                        np.array([100000., -157.46405841]))
      assert_array_almost_equal(pm_to_infinity, allaxes[1].lines[2].get_data())

      pm_to_phase = (np.array([6.07828691, 6.07828691]), np.array([-157.46405841, -180.]))
      assert_array_almost_equal(pm_to_phase, allaxes[1].lines[3].get_data())

      phase_to_infinity = (np.array([10., 10.]), np.array([1.00000000e-08, -1.80000000e+02]))
      assert_array_almost_equal(phase_to_infinity, allaxes[1].lines[4].get_data())

def suite():
   return unittest.TestLoader().loadTestsFromTestCase(TestTimeresp)

if __name__ == '__main__':
   unittest.main()
