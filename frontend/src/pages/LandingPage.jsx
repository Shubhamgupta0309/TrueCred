import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Lock, Users, TrendingUp, Star, ArrowRight, CheckCircle } from 'lucide-react';
import GlobeAnimation from '../components/landing/GlobeAnimation';

export default function LandingPage() {
  const navigate = useNavigate();
  const [selectedStep, setSelectedStep] = useState(0);

  const features = [
    {
      icon: Lock,
      title: 'Verified Credentials',
      description: 'OCR-powered with confidence scores',
    },
    {
      icon: Users,
      title: 'Direct Issuance',
      description: 'Institutions issue to you directly',
    },
    {
      icon: TrendingUp,
      title: 'Track Progress',
      description: 'Monitor requests in real-time',
    },
    {
      icon: Star,
      title: 'Blockchain Ready',
      description: 'Export for permanence',
    },
  ];

  const steps = [
    {
      number: '01',
      title: 'Request Credentials',
      description: 'Upload documents or request from your institution directly',
      color: 'from-blue-500 to-blue-600',
    },
    {
      number: '02',
      title: 'OCR Verification',
      description: 'Our AI verifies your credentials with confidence scores',
      color: 'from-purple-500 to-purple-600',
    },
    {
      number: '03',
      title: 'Institution Review',
      description: 'Your institution reviews and approves your credentials',
      color: 'from-emerald-500 to-emerald-600',
    },
    {
      number: '04',
      title: 'Build Portfolio',
      description: 'Track, share, and export your verifiable portfolio',
      color: 'from-amber-500 to-amber-600',
    },
  ];

  const testimonials = [
    {
      name: 'Raj Patel',
      role: 'Student',
      feedback: 'TrueCred made it so easy to manage my credentials. Institutions loved the verification process!',
      image: '👨‍🎓',
    },
    {
      name: 'Priya Singh',
      role: 'Professional',
      feedback: 'The blockchain export feature gives me peace of mind. My credentials are permanently secured.',
      image: '👩‍💼',
    },
    {
      name: 'Dr. Amit Kumar',
      role: 'University Admin',
      feedback: 'As an institution, TrueCred streamlined our credential issuance process significantly.',
      image: '👨‍🏫',
    },
  ];

  return (
    <div className="min-h-screen bg-[#06090e] overflow-x-hidden">
      {/* Navigation */}
      <motion.nav
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="fixed top-0 w-full z-50 bg-black bg-opacity-45 backdrop-blur-md border-b border-cyan-400 border-opacity-20"
      >
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <motion.div className="text-2xl font-black tracking-wide text-cyan-300">
            TRUECRED PLATFORM
          </motion.div>
          <div className="hidden md:flex items-center gap-8 text-xs font-semibold tracking-[0.18em] text-cyan-200">
            <a href="#case-study" className="hover:text-cyan-100 transition-colors">CASE STUDY</a>
            <a href="#platform" className="hover:text-cyan-100 transition-colors">THE PLATFORM</a>
            <a href="#contact" className="hover:text-cyan-100 transition-colors">CONTACT</a>
          </div>
        </div>
      </motion.nav>

      {/* Hero Section with Globe */}
      <section id="platform" className="relative min-h-screen pt-24 px-6 flex items-center">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(0,220,255,0.12),transparent_36%),radial-gradient(circle_at_80%_70%,rgba(0,160,255,0.12),transparent_30%)]" />
        <div className="relative max-w-7xl mx-auto w-full">
          <div className="grid grid-cols-1 lg:grid-cols-[0.95fr_1.25fr] gap-6 lg:gap-2 items-center">
            {/* Left: Content */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
              className="space-y-7"
            >
              <p className="text-cyan-300 text-sm font-semibold tracking-[0.2em] uppercase">Next Generation Credential Mobility</p>
              <h1 className="text-5xl md:text-7xl font-black leading-[0.92] text-cyan-200">
                OWN YOUR
                <span className="block text-cyan-400">DIGITAL TRUST</span>
              </h1>
              <p className="text-cyan-100/90 text-lg leading-relaxed max-w-xl">
                Request credentials from institutions, track OCR verification in real-time, and build your verifiable portfolio with the TrueCred Platform.
              </p>
              <div className="flex gap-4 pt-2">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => navigate('/auth')}
                  className="px-8 py-3 bg-cyan-400 text-slate-950 rounded-sm font-extrabold tracking-wide flex items-center gap-2 shadow-[0_0_30px_rgba(34,211,238,0.35)]"
                >
                  START NOW <ArrowRight className="w-4 h-4" />
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => document.getElementById('case-study')?.scrollIntoView({ behavior: 'smooth' })}
                  className="px-8 py-3 border border-cyan-400/70 text-cyan-200 rounded-sm font-bold hover:bg-cyan-400/10 transition-all"
                >
                  VIEW FLOW
                </motion.button>
              </div>
            </motion.div>

            {/* Right: Globe */}
            <motion.div
              initial={{ opacity: 0, scale: 0.92 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="translate-y-4 lg:translate-y-8"
            >
              <GlobeAnimation />
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="case-study" className="py-20 px-6 bg-cyan-500/5 backdrop-blur-sm border-y border-cyan-400/10">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold text-cyan-200 mb-4">
              Why Choose TrueCred?
            </h2>
            <p className="text-xl text-cyan-100/90">
              Everything you need to truly own your digital trust
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: i * 0.1 }}
                whileHover={{ y: -5 }}
                className="bg-white/5 backdrop-blur-md border border-cyan-300/20 rounded-xl p-6 hover:bg-cyan-400/10 transition-all"
              >
                <feature.icon className="w-10 h-10 text-cyan-300 mb-4" />
                <h3 className="text-lg font-bold text-cyan-100 mb-2">{feature.title}</h3>
                <p className="text-sm text-cyan-100/80">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Step-by-Step Process */}
      <section className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold text-cyan-200 mb-4">
              How It Works
            </h2>
            <p className="text-xl text-cyan-100/90">
              Simple, secure, and lightning-fast credential verification
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {steps.map((step, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: i * 0.1 }}
                onClick={() => setSelectedStep(i)}
                className="cursor-pointer group"
              >
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  className={`bg-gradient-to-br ${step.color} rounded-xl p-8 text-white h-full transform transition-all ${
                    selectedStep === i ? 'shadow-2xl scale-105' : 'shadow-lg'
                  }`}
                >
                  <div className="text-5xl font-bold opacity-20 mb-4">{step.number}</div>
                  <h3 className="text-2xl font-bold mb-3">{step.title}</h3>
                  <p className="text-white opacity-90">{step.description}</p>
                  <div className="mt-4 flex items-center gap-2 text-sm opacity-75">
                    {i < steps.length - 1 && (
                      <>
                        <CheckCircle className="w-4 h-4" />
                        <span>Next step →</span>
                      </>
                    )}
                  </div>
                </motion.div>
              </motion.div>
            ))}
          </div>

          {/* Process Details */}
          <motion.div
            key={selectedStep}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="mt-12 bg-white bg-opacity-10 backdrop-blur-md border border-white border-opacity-20 rounded-xl p-8"
          >
            <h3 className="text-2xl font-bold text-white mb-4">{steps[selectedStep].title}</h3>
            <p className="text-purple-200 text-lg mb-6">{steps[selectedStep].description}</p>
            <div className="space-y-3">
              <div className="flex items-center gap-3 text-purple-100">
                <div className="w-2 h-2 bg-purple-400 rounded-full" />
                <span>Fast and secure processing</span>
              </div>
              <div className="flex items-center gap-3 text-purple-100">
                <div className="w-2 h-2 bg-purple-400 rounded-full" />
                <span>Real-time status updates</span>
              </div>
              <div className="flex items-center gap-3 text-purple-100">
                <div className="w-2 h-2 bg-purple-400 rounded-full" />
                <span>Verified by OCR and institutions</span>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 px-6 bg-white bg-opacity-5 backdrop-blur-sm">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
              What Users Say
            </h2>
            <p className="text-xl text-purple-200">
              Join thousands of students and professionals trusting TrueCred
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: i * 0.1 }}
                className="bg-white bg-opacity-10 backdrop-blur-md border border-white border-opacity-20 rounded-xl p-8"
              >
                <div className="flex items-center gap-4 mb-6">
                  <div className="text-4xl">{testimonial.image}</div>
                  <div>
                    <h4 className="text-white font-bold">{testimonial.name}</h4>
                    <p className="text-sm text-purple-300">{testimonial.role}</p>
                  </div>
                </div>
                <p className="text-purple-100 italic">"{testimonial.feedback}"</p>
                <div className="mt-4 flex gap-1">
                  {[...Array(5)].map((_, i) => (
                    <span key={i} className="text-yellow-400">★</span>
                  ))}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="max-w-4xl mx-auto bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl p-12 text-center"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Ready to Own Your Digital Trust?
          </h2>
          <p className="text-xl text-purple-100 mb-8">
            Join us today and start building your verifiable credential portfolio
          </p>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => navigate('/auth')}
            className="px-12 py-4 bg-white text-purple-600 rounded-lg font-bold text-lg hover:shadow-xl transition-all"
          >
            Get Started Now
          </motion.button>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="border-t border-purple-400 border-opacity-20 py-8 px-6 bg-white bg-opacity-5">
        <div className="max-w-6xl mx-auto text-center text-purple-200">
          <p>&copy; 2026 TrueCred Platform. All rights reserved. Own your digital trust.</p>
        </div>
      </footer>
    </div>
  );
}
