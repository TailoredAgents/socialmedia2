import React, { useState, useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { 
  ChartBarIcon, 
  ClockIcon, 
  SparklesIcon, 
  UserGroupIcon,
  LightBulbIcon,
  ShieldCheckIcon,
  ArrowRightIcon,
  CheckCircleIcon,
  PlayCircleIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  RocketLaunchIcon,
  CogIcon,
  EyeIcon,
  ChatBubbleLeftRightIcon,
  BoltIcon,
  StarIcon,
  BuildingOfficeIcon,
  DevicePhoneMobileIcon,
  Bars3Icon,
  XMarkIcon
} from '@heroicons/react/24/outline'
import SEOHead from '../components/SEOHead'

const LandingPage = () => {
  const [searchParams] = useSearchParams()
  const [email, setEmail] = useState('')
  const [expandedFAQ, setExpandedFAQ] = useState(null)
  const [showVideo, setShowVideo] = useState(false)
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [showFloatingCTA, setShowFloatingCTA] = useState(false)
  const [isAnnualBilling, setIsAnnualBilling] = useState(true)
  const [currentTestimonial, setCurrentTestimonial] = useState(0)
  
  // Handle floating CTA visibility on scroll
  useEffect(() => {
    const handleScroll = () => {
      setShowFloatingCTA(window.scrollY > 800)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  // Auto-rotate testimonials
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTestimonial((prev) => (prev + 1) % 3) // Fixed number since we have 3 testimonials
    }, 5000)
    return () => clearInterval(timer)
  }, [])

  // Personalization from URL parameters
  const source = searchParams.get('utm_source') || ''
  const campaign = searchParams.get('utm_campaign') || ''

  // Features data
  const features = [
    {
      icon: RocketLaunchIcon,
      title: "Autonomous Autopilot Mode",
      description: "Let AI handle everything—research industry trends, generate content, schedule posts, and reply to messages based on your brand voice. No competitors offer this full hands-off experience.",
      highlight: "🚀 Unique in Market"
    },
    {
      icon: SparklesIcon,
      title: "AI-Powered Content Creation",
      description: "Use GPT-4o for text, Grok-2 Vision for images, Synthesia for short-form videos (Shorts/Reels), and ElevenLabs for sound matching. Optimized for all platforms.",
      highlight: "🎨 Multi-AI Suite"
    },
    {
      icon: ChartBarIcon,
      title: "Advanced Analytics & Insights",
      description: "Predictive forecasting, competitor dashboards, ROI tracking, and real-time recommendations to optimize your strategy.",
      highlight: "📊 AI-Powered Analytics"
    },
    {
      icon: CogIcon,
      title: "Seamless Integrations",
      description: "Connect to Salesforce, HubSpot, Shopify, Zapier, and more for automated workflows.",
      highlight: "🔗 Enterprise Ready"
    },
    {
      icon: ShieldCheckIcon,
      title: "Enterprise-Grade Security",
      description: "JWT auth, data encryption, audit logs, and compliance (GDPR/CCPA).",
      highlight: "🔒 Bank-Level Security"
    },
    {
      icon: DevicePhoneMobileIcon,
      title: "Mobile App & Collaboration",
      description: "On-the-go management plus team tools like real-time editing and approvals.",
      highlight: "📱 Team Features"
    }
  ]

  // How it works steps
  const steps = [
    {
      number: 1,
      title: "Configure Your Brand",
      description: "Set voice, industry, and goals in minutes",
      icon: UserGroupIcon
    },
    {
      number: 2,
      title: "AI Researches Trends",
      description: "Daily scans for relevant topics in your industry",
      icon: EyeIcon
    },
    {
      number: 3,
      title: "Creates & Schedules Content",
      description: "Generates posts/images/videos and publishes autonomously",
      icon: SparklesIcon
    },
    {
      number: 4,
      title: "Handles Engagement",
      description: "AI responds to comments/messages with escalation if needed",
      icon: ChatBubbleLeftRightIcon
    },
    {
      number: 5,
      title: "Optimizes with Analytics",
      description: "Self-adjusts based on performance data",
      icon: BoltIcon
    }
  ]

  // Pricing tiers
  const pricingTiers = [
    {
      name: "Starter",
      price: isAnnualBilling ? "$59" : "$74",
      originalPrice: isAnnualBilling ? "$708/year" : "$74/month",
      period: isAnnualBilling ? "month (billed annually)" : "month",
      description: "Ideal for solopreneurs or small teams starting with hands-off social management",
      features: [
        "Up to 5 social profiles (X, Meta, LinkedIn, TikTok, YouTube, Threads)",
        "Basic AI content generation (GPT-4o-mini, limited Grok-2 Vision)",
        "Limited autopilot mode with daily automated posts",
        "Social inbox monitoring (no AI responses)",
        "Basic analytics with AI optimization recommendations",
        "Content repurposing and recycling tools",
        "Multi-language support (up to 10 languages)",
        "Customizable dashboards and UI themes",
        "Automated backups and recovery",
        "1 user account"
      ],
      cta: "Start 14-Day Free Trial",
      popular: false,
      savings: isAnnualBilling ? "Save 20% annually" : null
    },
    {
      name: "Pro",
      price: isAnnualBilling ? "$149" : "$186",
      originalPrice: isAnnualBilling ? "$1,788/year" : "$186/month",
      period: isAnnualBilling ? "month (billed annually)" : "month",
      description: "Perfect for growing SMBs and agencies needing scalable, autonomous features",
      features: [
        "Unlimited social profiles across all platforms",
        "Full AI suite (GPT-4o, Grok-2 Vision, Synthesia/Runway ML videos)",
        "Enhanced autopilot mode with auto-ad campaigns & trend forecasting",
        "AI-powered social inbox responses and chatbots",
        "Advanced analytics with competitor analysis & ROI tracking",
        "CRM integrations (Salesforce, HubSpot, Shopify)",
        "Third-party tool integrations (Zapier-like automation)",
        "Mobile app for on-the-go management",
        "Enhanced collaboration tools & approval workflows",
        "Up to 5 users and 5 workspaces"
      ],
      cta: "Start 14-Day Free Trial",
      popular: true,
      savings: isAnnualBilling ? "Save 20% annually" : null
    },
    {
      name: "Enterprise",
      price: isAnnualBilling ? "$499" : "$624",
      originalPrice: isAnnualBilling ? "$5,988/year" : "$624/month",
      period: isAnnualBilling ? "month (billed annually)" : "month",
      description: "Designed for high-scale operations with enterprise-grade security and customization",
      features: [
        "All Pro features with unlimited users & workspaces",
        "Complete autopilot with predictive analytics integration",
        "Influencer & affiliate management integrations",
        "Auto-scaling infrastructure for high-volume use",
        "Advanced audit & compliance tools (CCPA/GDPR)",
        "White-labeling and custom API access",
        "Priority support with dedicated account manager",
        "Custom training sessions included",
        "Unlimited add-ons and integrations",
        "Enterprise-grade security & customization"
      ],
      cta: "Contact Sales",
      popular: false,
      savings: isAnnualBilling ? "Save 20% annually" : null
    }
  ]

  // Testimonials
  const testimonials = [
    {
      quote: "Lily AI saved us 90% on social media time—autopilot is a game-changer! Our engagement increased 300% while we focus on core business.",
      author: "Sarah Chen",
      role: "Founder",
      company: "TechStart Solutions",
      avatar: "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=64&h=64&fit=crop&crop=face",
      rating: 5
    },
    {
      quote: "Unique features like Grok-2 Vision make our content stand out. Clients love the consistent, high-quality posts across all platforms.",
      author: "Marcus Rodriguez",
      role: "Marketing Director",
      company: "Digital Growth Agency",
      avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=64&h=64&fit=crop&crop=face",
      rating: 5
    },
    {
      quote: "The autopilot mode is incredible. It handles our entire social media strategy while we sleep. ROI increased by 250% in 3 months.",
      author: "Emily Johnson",
      role: "CMO",
      company: "EcoStyle Brand",
      avatar: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=64&h=64&fit=crop&crop=face",
      rating: 5
    }
  ]

  // FAQ items
  const faqs = [
    {
      question: "What makes Lily AI different from other social media tools?",
      answer: "Lily AI is the only platform offering full autonomous autopilot mode—no human oversight needed. Our AI researches trends, creates content, schedules posts, and handles engagement completely on its own. Competitors require constant manual input."
    },
    {
      question: "Which social media platforms are supported?",
      answer: "We support all major platforms: X (Twitter), Meta (Facebook & Instagram), LinkedIn, TikTok, YouTube, and Threads. More platforms are added regularly based on user demand."
    },
    {
      question: "How secure is my data and social media accounts?",
      answer: "Enterprise-grade security with JWT authentication, end-to-end encryption, audit logs, and full GDPR/CCPA compliance. Your data is more secure with us than managing accounts manually."
    },
    {
      question: "Can I cancel my subscription anytime?",
      answer: "Yes, absolutely! No lock-in contracts. Cancel anytime with one click. You'll retain access until your current billing period ends."
    },
    {
      question: "How does the 14-day free trial work?",
      answer: "Full access to all features for 14 days. No credit card required to start. If you love it (which you will), seamlessly upgrade to continue. Cancel anytime during trial with zero charges."
    },
    {
      question: "What AI models power Lily AI?",
      answer: "We use the latest AI: GPT-4o for text, Grok-2 Vision for images, Synthesia/Runway ML for videos, and ElevenLabs for voice. This multi-AI approach ensures best-in-class content across all formats."
    }
  ]

  const handleEmailSubmit = (e) => {
    e.preventDefault()
    window.location.href = `/register?email=${encodeURIComponent(email)}`
  }

  const scrollToSection = (sectionId) => {
    document.getElementById(sectionId)?.scrollIntoView({ behavior: 'smooth' })
    setIsMenuOpen(false)
  }

  return (
    <div className="min-h-screen bg-white">
      <SEOHead />
      
      {/* Sticky Navigation */}
      <nav className="fixed top-0 left-0 right-0 bg-white/95 backdrop-blur-sm border-b border-gray-200 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Link to="/" className="flex items-center">
                <SparklesIcon className="h-8 w-8 text-blue-600" />
                <span className="ml-2 text-2xl font-bold text-gray-900">Lily AI</span>
              </Link>
            </div>
            
            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              <button onClick={() => scrollToSection('features')} className="text-gray-600 hover:text-blue-600 transition-colors">
                Features
              </button>
              <button onClick={() => scrollToSection('how-it-works')} className="text-gray-600 hover:text-blue-600 transition-colors">
                How It Works
              </button>
              <button onClick={() => scrollToSection('pricing')} className="text-gray-600 hover:text-blue-600 transition-colors">
                Pricing
              </button>
              <Link to="/login" className="text-gray-600 hover:text-blue-600 transition-colors">
                Login
              </Link>
              <Link to="/register" className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors">
                Start Free Trial
              </Link>
            </div>

            {/* Mobile menu button */}
            <div className="md:hidden">
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="text-gray-600 hover:text-blue-600"
              >
                {isMenuOpen ? <XMarkIcon className="h-6 w-6" /> : <Bars3Icon className="h-6 w-6" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden bg-white border-t border-gray-200">
            <div className="px-4 py-2 space-y-3">
              <button onClick={() => scrollToSection('features')} className="block text-gray-600 hover:text-blue-600">
                Features
              </button>
              <button onClick={() => scrollToSection('how-it-works')} className="block text-gray-600 hover:text-blue-600">
                How It Works
              </button>
              <button onClick={() => scrollToSection('pricing')} className="block text-gray-600 hover:text-blue-600">
                Pricing
              </button>
              <Link to="/login" className="block text-gray-600 hover:text-blue-600">
                Login
              </Link>
              <Link to="/register" className="block bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium text-center">
                Start Free Trial
              </Link>
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section className="pt-20 pb-16 bg-gradient-to-br from-blue-50 via-white to-indigo-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            {/* Urgency Banner */}
            <div className="inline-flex items-center px-4 py-2 rounded-full bg-green-100 text-green-800 text-sm font-medium mb-6">
              <BoltIcon className="h-4 w-4 mr-2" />
              Limited Time: 14-Day Free Trial - No Credit Card Required
            </div>
            
            {/* Main Headline */}
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
              Revolutionize Your Social Media with{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">
                Lily AI's Autonomous Autopilot
              </span>
            </h1>
            
            {/* Subheadline */}
            <h2 className="text-xl sm:text-2xl text-gray-600 mb-8 max-w-4xl mx-auto">
              AI-powered management that researches trends, creates engaging content, schedules posts, 
              and handles responses—all on autopilot. Save 90% time for SMBs.
            </h2>
            
            {/* Key Benefits */}
            <div className="flex flex-col sm:flex-row gap-6 justify-center items-center mb-10">
              <div className="flex items-center text-gray-700">
                <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2" />
                <span className="font-medium">Unique in the market: No human oversight needed</span>
              </div>
              <div className="flex items-center text-gray-700">
                <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2" />
                <span className="font-medium">Powered by GPT-4o, Grok-2 Vision, and more</span>
              </div>
              <div className="flex items-center text-gray-700">
                <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2" />
                <span className="font-medium">Supports X, Meta, LinkedIn, TikTok, YouTube, Threads</span>
              </div>
            </div>

            {/* Email Capture & CTA */}
            <div className="max-w-md mx-auto mb-8">
              <form onSubmit={handleEmailSubmit} className="flex gap-3">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email"
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-center"
                  required
                />
                <button
                  type="submit"
                  className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-colors flex items-center"
                >
                  Start Free Trial
                  <ArrowRightIcon className="ml-2 h-4 w-4" />
                </button>
              </form>
              <p className="text-sm text-gray-500 mt-2">
                14-day free trial • No credit card required • Cancel anytime
              </p>
            </div>

            {/* Demo Video Button */}
            <button
              onClick={() => setShowVideo(true)}
              className="inline-flex items-center px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors mb-12"
            >
              <PlayCircleIcon className="h-5 w-5 mr-2" />
              Watch Autopilot Demo (30s)
            </button>

            {/* Trust Badges */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 items-center opacity-60">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">5,000+</div>
                <div className="text-sm text-gray-600">Active Users</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">90%</div>
                <div className="text-sm text-gray-600">Time Saved</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">300%</div>
                <div className="text-sm text-gray-600">Engagement Boost</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">24/7</div>
                <div className="text-sm text-gray-600">Autopilot Mode</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Powerful Features That Set Us Apart
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Discover the unique capabilities that make Lily AI the most advanced social media management platform
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="bg-white p-8 rounded-xl shadow-sm hover:shadow-md transition-shadow border border-gray-100">
                <div className="flex items-center mb-4">
                  <div className="p-3 bg-blue-100 rounded-lg">
                    <feature.icon className="h-6 w-6 text-blue-600" />
                  </div>
                  <span className="ml-3 text-sm font-medium text-green-600 bg-green-100 px-2 py-1 rounded-full">
                    {feature.highlight}
                  </span>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
          
          <div className="text-center mt-12">
            <button
              onClick={() => setShowVideo(true)}
              className="inline-flex items-center px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors"
            >
              See Features in Action
              <PlayCircleIcon className="ml-2 h-5 w-5" />
            </button>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              How Lily AI Autopilot Works
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Set it once, let AI handle everything. Here's how our autonomous system transforms your social media presence
            </p>
          </div>

          {/* Desktop Timeline */}
          <div className="hidden lg:block">
            <div className="relative">
              <div className="absolute left-1/2 transform -translate-x-px h-full w-0.5 bg-gray-300"></div>
              {steps.map((step, index) => (
                <div key={index} className={`relative flex items-center ${index % 2 === 0 ? 'justify-start' : 'justify-end'} mb-8`}>
                  <div className={`w-5/12 ${index % 2 === 0 ? 'pr-8 text-right' : 'pl-8 text-left'}`}>
                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">{step.title}</h3>
                      <p className="text-gray-600">{step.description}</p>
                    </div>
                  </div>
                  <div className="absolute left-1/2 transform -translate-x-1/2 w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center">
                    <step.icon className="h-6 w-6 text-white" />
                  </div>
                  <div className={`w-5/12 ${index % 2 === 0 ? 'pl-8' : 'pr-8'}`}>
                    <div className={`text-6xl font-bold text-blue-100 ${index % 2 === 0 ? 'text-left' : 'text-right'}`}>
                      {step.number}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Mobile Timeline */}
          <div className="lg:hidden space-y-8">
            {steps.map((step, index) => (
              <div key={index} className="flex items-start">
                <div className="flex-shrink-0 w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center mr-4">
                  <step.icon className="h-6 w-6 text-white" />
                </div>
                <div className="flex-grow">
                  <div className="flex items-center mb-2">
                    <span className="text-2xl font-bold text-blue-600 mr-3">0{step.number}</span>
                    <h3 className="text-lg font-semibold text-gray-900">{step.title}</h3>
                  </div>
                  <p className="text-gray-600">{step.description}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="text-center mt-12">
            <div className="bg-blue-50 rounded-xl p-8 max-w-2xl mx-auto">
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Ready to See It In Action?</h3>
              <p className="text-gray-600 mb-6">
                Watch our interactive demo showing real autopilot functionality
              </p>
              <button
                onClick={() => setShowVideo(true)}
                className="inline-flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors"
              >
                <PlayCircleIcon className="h-5 w-5 mr-2" />
                Interactive Demo
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Choose Your Plan
            </h2>
            <p className="text-xl text-gray-600 mb-8">
              All plans come with a 14-day free trial. No credit card required.
            </p>
            
            {/* Billing Toggle */}
            <div className="flex items-center justify-center mb-12">
              <span className={`mr-3 ${!isAnnualBilling ? 'text-gray-900 font-medium' : 'text-gray-500'}`}>Monthly</span>
              <button
                onClick={() => setIsAnnualBilling(!isAnnualBilling)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${isAnnualBilling ? 'bg-blue-600' : 'bg-gray-200'}`}
              >
                <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${isAnnualBilling ? 'translate-x-6' : 'translate-x-1'}`} />
              </button>
              <span className={`ml-3 ${isAnnualBilling ? 'text-gray-900 font-medium' : 'text-gray-500'}`}>
                Annual
                <span className="ml-1 text-green-600 font-semibold">(Save 20%)</span>
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {pricingTiers.map((tier, index) => (
              <div
                key={index}
                className={`bg-white rounded-xl p-8 shadow-sm relative ${
                  tier.popular ? 'ring-2 ring-blue-600 transform scale-105' : 'border border-gray-200'
                }`}
              >
                {tier.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span className="bg-blue-600 text-white px-4 py-1 rounded-full text-sm font-medium">
                      Most Popular
                    </span>
                  </div>
                )}
                
                <div className="text-center mb-8">
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">{tier.name}</h3>
                  <div className="mb-4">
                    <span className="text-4xl font-bold text-gray-900">{tier.price}</span>
                    <span className="text-gray-600">/{tier.period}</span>
                  </div>
                  <p className="text-gray-600 text-sm mb-4">{tier.description}</p>
                  {tier.savings && (
                    <p className="text-green-600 text-sm font-medium bg-green-50 px-3 py-1 rounded-full inline-block">
                      {tier.savings}
                    </p>
                  )}
                </div>
                
                <ul className="space-y-3 mb-8">
                  {tier.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-start">
                      <CheckCircleIcon className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
                      <span className="ml-3 text-gray-600 text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>
                
                <Link
                  to={tier.cta === "Contact Sales" ? "/contact" : "/register"}
                  className={`w-full px-6 py-3 rounded-lg font-semibold text-center block transition-colors ${
                    tier.popular
                      ? 'bg-blue-600 hover:bg-blue-700 text-white'
                      : 'bg-gray-100 hover:bg-gray-200 text-gray-900'
                  }`}
                >
                  {tier.cta}
                </Link>
              </div>
            ))}
          </div>
          
          <div className="text-center mt-8">
            <p className="text-gray-600">
              All plans include 14-day free trial • Annual billing saves 20% • No setup fees • Cancel anytime
            </p>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              What Our Customers Say
            </h2>
            <p className="text-xl text-gray-600">
              Join thousands of businesses already saving time with Lily AI
            </p>
          </div>

          <div className="relative max-w-4xl mx-auto">
            <div className="bg-gray-50 rounded-2xl p-8 text-center">
              <div className="flex justify-center mb-4">
                {[...Array(testimonials[currentTestimonial].rating)].map((_, i) => (
                  <StarIcon key={i} className="h-5 w-5 text-yellow-400 fill-current" />
                ))}
              </div>
              
              <blockquote className="text-xl text-gray-700 mb-6">
                "{testimonials[currentTestimonial].quote}"
              </blockquote>
              
              <div className="flex items-center justify-center">
                <img
                  src={testimonials[currentTestimonial].avatar}
                  alt={testimonials[currentTestimonial].author}
                  className="w-12 h-12 rounded-full mr-4"
                />
                <div className="text-left">
                  <div className="font-semibold text-gray-900">{testimonials[currentTestimonial].author}</div>
                  <div className="text-gray-600">{testimonials[currentTestimonial].role}, {testimonials[currentTestimonial].company}</div>
                </div>
              </div>
            </div>

            {/* Testimonial Navigation Dots */}
            <div className="flex justify-center mt-6 space-x-2">
              {testimonials.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentTestimonial(index)}
                  className={`w-3 h-3 rounded-full transition-colors ${
                    index === currentTestimonial ? 'bg-blue-600' : 'bg-gray-300'
                  }`}
                />
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Frequently Asked Questions
            </h2>
            <p className="text-xl text-gray-600">
              Get answers to common questions about Lily AI
            </p>
          </div>
          
          <div className="space-y-4">
            {faqs.map((faq, index) => (
              <div key={index} className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                <button
                  onClick={() => setExpandedFAQ(expandedFAQ === index ? null : index)}
                  className="w-full px-6 py-4 text-left flex items-center justify-between hover:bg-gray-50 transition-colors"
                >
                  <span className="font-medium text-gray-900">{faq.question}</span>
                  {expandedFAQ === index ? (
                    <ChevronUpIcon className="h-5 w-5 text-gray-500" />
                  ) : (
                    <ChevronDownIcon className="h-5 w-5 text-gray-500" />
                  )}
                </button>
                {expandedFAQ === index && (
                  <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
                    <p className="text-gray-700">{faq.answer}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-indigo-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
            Ready to Transform Your Social Media?
          </h2>
          <p className="text-xl text-blue-100 mb-10">
            Join 5,000+ businesses already using Lily AI to dominate social media with full autopilot
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link
              to="/register"
              className="bg-white hover:bg-gray-100 text-blue-600 px-8 py-4 rounded-lg text-lg font-semibold transition-colors inline-flex items-center"
            >
              Start Your 14-Day Free Trial
              <ArrowRightIcon className="ml-2 h-5 w-5" />
            </Link>
            <button
              onClick={() => setShowVideo(true)}
              className="border border-white text-white hover:bg-white hover:text-blue-600 px-8 py-4 rounded-lg text-lg font-semibold transition-colors inline-flex items-center"
            >
              <PlayCircleIcon className="mr-2 h-5 w-5" />
              Watch Demo First
            </button>
          </div>
          <p className="mt-6 text-blue-200 text-sm">
            No credit card required • Full access for 14 days • Cancel anytime
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="col-span-1 md:col-span-2">
              <div className="flex items-center mb-4">
                <SparklesIcon className="h-8 w-8 text-blue-400" />
                <span className="ml-2 text-2xl font-bold text-white">Lily AI</span>
              </div>
              <p className="text-gray-300 max-w-md mb-6">
                The most intelligent social media management platform. 
                Create, schedule, and optimize your content with autonomous AI.
              </p>
              <div className="flex space-x-4">
                {/* Social Media Icons - Replace with actual links */}
                <a href="#" className="text-gray-400 hover:text-white transition-colors">
                  <span className="sr-only">Twitter</span>
                  <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" />
                  </svg>
                </a>
              </div>
            </div>
            
            <div>
              <h4 className="text-lg font-semibold text-white mb-4">Product</h4>
              <ul className="space-y-2">
                <li><button onClick={() => scrollToSection('features')} className="text-gray-300 hover:text-white transition-colors">Features</button></li>
                <li><button onClick={() => scrollToSection('pricing')} className="text-gray-300 hover:text-white transition-colors">Pricing</button></li>
                <li><Link to="/login" className="text-gray-300 hover:text-white transition-colors">Sign In</Link></li>
                <li><Link to="/register" className="text-gray-300 hover:text-white transition-colors">Free Trial</Link></li>
              </ul>
            </div>
            
            <div>
              <h4 className="text-lg font-semibold text-white mb-4">Company</h4>
              <ul className="space-y-2">
                <li><a href="#" className="text-gray-300 hover:text-white transition-colors">About</a></li>
                <li><a href="#" className="text-gray-300 hover:text-white transition-colors">Privacy Policy</a></li>
                <li><a href="#" className="text-gray-300 hover:text-white transition-colors">Terms of Service</a></li>
                <li><a href="#" className="text-gray-300 hover:text-white transition-colors">Contact</a></li>
              </ul>
            </div>
          </div>
          
          <div className="mt-12 pt-8 border-t border-gray-700">
            <div className="flex flex-col md:flex-row justify-between items-center">
              <p className="text-gray-400">
                © 2025 Lily AI. All rights reserved.
              </p>
              <div className="mt-4 md:mt-0">
                <Link
                  to="/register"
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors inline-flex items-center"
                >
                  Ready to Automate? Start Free Trial
                  <ArrowRightIcon className="ml-2 h-4 w-4" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </footer>

      {/* Floating CTA Button */}
      {showFloatingCTA && (
        <div className="fixed bottom-6 right-6 z-50">
          <Link
            to="/register"
            className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-full shadow-lg font-semibold transition-all transform hover:scale-105 inline-flex items-center"
          >
            Start Free Trial
            <ArrowRightIcon className="ml-2 h-4 w-4" />
          </Link>
        </div>
      )}

      {/* Video Modal */}
      {showVideo && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-75" onClick={() => setShowVideo(false)}>
          <div className="bg-white p-4 rounded-lg max-w-4xl w-full mx-4" onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Lily AI Autopilot Demo</h3>
              <button
                onClick={() => setShowVideo(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>
            <div className="aspect-video bg-gray-200 flex items-center justify-center rounded">
              {/* Replace with actual video embed */}
              <div className="text-center">
                <PlayCircleIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">Interactive Autopilot Demo</p>
                <p className="text-sm text-gray-500 mt-2">Video integration coming soon</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default LandingPage