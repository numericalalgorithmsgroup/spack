# Copyright 2013-2020 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# ----------------------------------------------------------------------------
# If you submit this package back to Spack as a pull request,
# please first remove this boilerplate and all FIXME comments.
#
# This is a template package file for Spack.  We've put "FIXME"
# next to all the things you'll want to change. Once you've handled
# them, you can save this file and test your package like this:
#
#     spack install mxnet
#
# You can edit this file again by typing:
#
#     spack edit mxnet
#
# See the Spack documentation for more information on packaging.
# ----------------------------------------------------------------------------

import inspect

from spack import *
from llnl.util.filesystem import working_dir

class Mxnet(CMakePackage, CudaPackage):
    """FIXME: Put a proper description of your package here."""

    homepage = "http://mxnet.io"
    url      = "https://archive.apache.org/dist/incubator/mxnet/1.6.0/apache-mxnet-src-1.6.0-incubating.tar.gz"

    maintainers = ['adamjstewart', 'ptooley']

    version('1.7.0', sha256='1d20c9be7d16ccb4e830e9ee3406796efaf96b0d93414d676337b64bc59ced18')
    version('1.6.0', sha256='01eb06069c90f33469c7354946261b0a94824bbaf819fd5d5a7318e8ee596def')

    variant('opencv', default=True, description="Use OpenCV for vision support")
    variant('mkldnn', default=False, description="Use the MKLDNN extensions")
    variant('python', default=True, description="Build Python (gluon) interface")
    variant('nccl', default=True, description="Use NVIDIA NCCL communications layer")
    variant('openmp', default=False, description="Enable OpenMP parallelism support")
    variant('profiler', default=False, description="Enable builtin profiler support")

    depends_on('cmake@3.13:')
    depends_on('blas')
    depends_on('lapack')

    depends_on('opencv+core+imgproc+highgui+jpeg+png+tiff~eigen~ipp@3.0:', when='+opencv')
    depends_on('nccl', when="+nccl")
    depends_on('intel-mkl', when="+mkldnn")

    # Divined from MXNet available builds
    depends_on('cuda@7.5.0:11.0.99', when="@1.7.0 +cuda")
    depends_on('cuda@7.5.0:10.2.99', when="@1.6.0 +cuda")
    depends_on('cuda@7.5.0:10.1.99', when="@1.5.1 +cuda")

    patch('CUDA11_fix_cub_supplied.patch', when='@1.6.0:1.7.0')
    patch('parallell_shuffle.patch', when='@1.6.0')

    def cmake_args(self):
        args = [
                '-DCMAKE_BUILD_TYPE=RelwithDebInfo',
                self.define_from_variant('-DUSE_CUDA', 'cuda'),
                self.define_from_variant('-DUSE_OPENCV', 'opencv'),
                self.define_from_variant('-DUSE_MKLDNN', 'mkldnn'),
                self.define_from_variant('-DUSE_OPENMP', 'openmp'),
                self.define_from_variant('-DUSE_PROFILER', 'profiler')
                ]

        if '+cuda' in self.spec:
            # Need to format as 6.2 7.0 etc.
            mxnet_arch = ' '.join(
                ['.'.join(arch) for arch in self.spec.variants['cuda_arch'].value])
            args.append('-DMXNET_CUDA_ARCH='+mxnet_arch)


        if 'openblas' in self.spec:
            args.append('-DBLAS=open')
        elif 'atlas' in self.spec:
            args.append('-DBLAS=atlas')
        elif 'intel-mkl' in self.spec:
            args.append('-DBLAS=mkl')
        else:
            raise InstallError("Unsupported blas provider - need MKL, Openblas or Atlas")

        return args

    def install(self, spec, prefix):
        # First do library install
        with working_dir(self.build_directory):
            inspect.getmodule(self).make(*self.install_targets)

        # Now deal with interfaces
        if '+python' in spec:
            python = which('python')
            python('python/setup.py', 'install', '--prefix=' + prefix)
