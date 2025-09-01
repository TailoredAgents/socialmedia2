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
  RocketLaunchIcon
} from '@heroicons/react/24/outline'

const LandingPage = () => {
  const [searchParams] = useSearchParams()
  const [email, setEmail] = useState('')
  const [expandedFAQ, setExpandedFAQ] = useState(null)
  const [showVideo, setShowVideo] = useState(false)
  
  // Personalization from URL parameters (from ads)
  const source = searchParams.get('utm_source') || ''
  const campaign = searchParams.get('utm_campaign') || ''
  // Problem-Solution pairs for new section
  const problems = [
    {
      problem: "Spending hours creating social media content?",
      solution: "AI generates engaging posts in seconds with GPT-4o"
    },
    {
      problem: "Struggling to maintain consistent posting?",
      solution: "Full autopilot mode handles everything 24/7"
    },
    {
      problem: "Missing important customer interactions?",
      solution: "AI responds to comments and messages automatically"
    },
    {
      problem: "Can't track what's working?",
      solution: "Real-time analytics show exactly what drives engagement"
    }
  ]

  const features = [
    {
      icon: SparklesIcon,
      title: "AI-Powered Content Creation",
      description: "Generate engaging social media content with GPT-4o and Grok-2 Vision that understands your brand voice.",
      benefit: "Save 10+ hours per week"
    },
    {
      icon: RocketLaunchIcon,
      title: "Full Autopilot Mode",
      description: "Set it once, runs forever. Posts, responds, and adapts automatically without any manual intervention.",
      benefit: "True hands-off automation"
    },
    {
      icon: ChartBarIcon,
      title: "Advanced Analytics",
      description: "Track performance, analyze engagement patterns, and get AI-powered insights to grow your social presence.",
      benefit: "2x your engagement rate"
    },
    {
      icon: UserGroupIcon,
      title: "Multi-Platform Management",
      description: "Manage X (Twitter), Instagram, and Facebook from one unified dashboard with OAuth integration.",
      benefit: "No more platform juggling"
    },
    {
      icon: LightBulbIcon,
      title: "Content Memory System",
      description: "AI remembers your past content and audience preferences to create more relevant and engaging posts.",
      benefit: "Consistent brand voice"
    },
    {
      icon: ShieldCheckIcon,
      title: "Enterprise Security",
      description: "Bank-level security with encrypted storage and multi-tenant architecture for team collaboration.",
      benefit: "SOC 2 compliant"
    }
  ]

  const testimonials = [
    {
      quote: "Lily AI transformed our social media strategy. We've seen a 40% increase in engagement in just 2 weeks!",
      author: "Sarah Chen",
      role: "Marketing Director",
      company: "TechFlow Inc.",
      metric: "+40% Engagement"
    },
    {
      quote: "The AI content generation with autopilot mode is like having a team of 5 people working 24/7.",
      author: "Marcus Rodriguez",
      role: "Founder",
      company: "GrowthLabs",
      metric: "5x Productivity"
    },
    {
      quote: "ROI positive in the first month. Best investment we've made for our social media.",
      author: "Emily Watson",
      role: "Content Manager",
      company: "InnovateNow",
      metric: "312% ROI"
    }
  ]

  const pricingTiers = [
    {
      name: "Starter",
      price: "$74",
      period: "month",
      annualPrice: "$59",
      yearlyPrice: "$708",
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
      cta: "Start 14-Day Trial",
      popular: false,
      savings: "Save 20% with annual billing ($59/mo)"
    },
    {
      name: "Pro",
      price: "$186",
      period: "month", 
      annualPrice: "$149",
      yearlyPrice: "$1,788",
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
      cta: "Start 14-Day Trial",
      popular: true,
      savings: "Save 20% with annual billing ($149/mo)"
    },
    {
      name: "Enterprise",
      price: "$624",
      period: "month",
      annualPrice: "$499", 
      yearlyPrice: "$5,988",
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
      savings: "Save 20% with annual billing ($499/mo)"
    }
  ]

  // FAQ items
  const faqs = [
    {
      question: "How does Lily AI integrate with my social accounts?",
      answer: "Lily uses secure OAuth connections to link with your X, Facebook, and Instagram accounts. Your login credentials are never stored – only secure tokens that you can revoke anytime."
    },
    {
      question: "What AI models power Lily?",
      answer: "We use OpenAI's GPT-4o for content generation, xAI's Grok-2 Vision for images, and custom fine-tuned models for your specific brand voice."
    },
    {
      question: "Is there really a free trial?",
      answer: "Yes! 14 days, full access, no credit card required. We're confident you'll love Lily."
    },
    {
      question: "How quickly can I get started?",
      answer: "Under 5 minutes. Sign up, connect your accounts, tell us about your business, and enable autopilot."
    },
    {
      question: "Can I cancel anytime?",
      answer: "Absolutely. No contracts, no hidden fees. Cancel with one click."
    },
    {
      question: "What makes Lily different from other tools?",
      answer: "True autopilot mode. While others require constant input, Lily actually runs your social media autonomously."
    }
  ]

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="bg-white shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-2xl font-bold text-indigo-600">Lily AI</h1>
              </div>
              <div className="hidden md:block ml-10">
                <div className="flex items-baseline space-x-8">
                  <a href="#features" className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium">Features</a>
                  <a href="#testimonials" className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium">Testimonials</a>
                  <a href="#pricing" className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium">Pricing</a>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                to="/login"
                className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-20 pb-16 sm:pt-24 sm:pb-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 leading-tight">
              AI-Powered Social Media
              <span className="text-indigo-600 block">Made Simple</span>
            </h1>
            <p className="mt-6 text-xl text-gray-600 max-w-3xl mx-auto">
              Transform your social media presence with intelligent content creation, 
              automated scheduling, and powerful analytics. Let AI handle the heavy lifting 
              while you focus on growing your business.
            </p>
            <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/register"
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-8 py-4 rounded-lg text-lg font-semibold transition-colors inline-flex items-center justify-center"
              >
                Start Free Trial
                <ArrowRightIcon className="ml-2 h-5 w-5" />
              </Link>
              <Link
                to="/login"
                className="border-2 border-gray-300 hover:border-gray-400 text-gray-700 px-8 py-4 rounded-lg text-lg font-semibold transition-colors"
              >
                Sign In
              </Link>
            </div>
            <p className="mt-4 text-sm text-gray-500">
              No credit card required • 14-day free trial • Cancel anytime
            </p>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">
              Everything you need to dominate social media
            </h2>
            <p className="mt-4 text-xl text-gray-600">
              Powerful features designed to scale your social media presence
            </p>
          </div>
          <div className="mt-16 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="bg-white rounded-xl p-8 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-center justify-center w-12 h-12 bg-indigo-100 rounded-lg">
                  <feature.icon className="h-6 w-6 text-indigo-600" />
                </div>
                <h3 className="mt-6 text-xl font-semibold text-gray-900">{feature.title}</h3>
                <p className="mt-4 text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">
              Trusted by thousands of businesses
            </h2>
            <p className="mt-4 text-xl text-gray-600">
              See what our customers are saying about Lily AI
            </p>
          </div>
          <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="bg-white rounded-xl p-8 shadow-sm">
                <p className="text-gray-600 text-lg italic">"{testimonial.quote}"</p>
                <div className="mt-6">
                  <div className="font-semibold text-gray-900">{testimonial.author}</div>
                  <div className="text-gray-600">{testimonial.role}</div>
                  <div className="text-indigo-600 font-medium">{testimonial.company}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">
              Simple, transparent pricing
            </h2>
            <p className="mt-4 text-xl text-gray-600">
              Choose the plan that's right for your business
            </p>
          </div>
          <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
            {pricingTiers.map((tier, index) => (
              <div
                key={index}
                className={`bg-white rounded-xl p-8 shadow-sm relative ${
                  tier.popular ? 'ring-2 ring-indigo-600 transform scale-105' : ''
                }`}
              >
                {tier.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span className="bg-indigo-600 text-white px-4 py-1 rounded-full text-sm font-medium">
                      Most Popular
                    </span>
                  </div>
                )}
                <div className="text-center">
                  <h3 className="text-2xl font-bold text-gray-900">{tier.name}</h3>
                  <div className="mt-4">
                    <span className="text-4xl font-bold text-gray-900">{tier.price}</span>
                    <span className="text-gray-600">{tier.period.startsWith('/') ? tier.period : `/${tier.period}`}</span>
                  </div>
                  <p className="mt-4 text-gray-600">{tier.description}</p>
                  {tier.savings && (
                    <p className="mt-2 text-green-600 text-sm font-medium">{tier.savings}</p>
                  )}
                </div>
                <ul className="mt-8 space-y-4">
                  {tier.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-center">
                      <CheckCircleIcon className="h-5 w-5 text-indigo-600 flex-shrink-0" />
                      <span className="ml-3 text-gray-600">{feature}</span>
                    </li>
                  ))}
                </ul>
                <div className="mt-8">
                  <Link
                    to="/register"
                    className={`w-full px-6 py-3 rounded-lg font-semibold text-center block transition-colors ${
                      tier.popular
                        ? 'bg-indigo-600 hover:bg-indigo-700 text-white'
                        : 'bg-gray-100 hover:bg-gray-200 text-gray-900'
                    }`}
                  >
                    {tier.cta}
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-12">
            Frequently Asked Questions
          </h2>
          <div className="space-y-4">
            {faqs.map((faq, i) => (
              <div key={i} className="border border-gray-200 rounded-lg overflow-hidden">
                <button
                  onClick={() => setExpandedFAQ(expandedFAQ === i ? null : i)}
                  className="w-full px-6 py-4 text-left flex items-center justify-between hover:bg-gray-50 transition-colors"
                >
                  <span className="font-medium text-gray-900">{faq.question}</span>
                  {expandedFAQ === i ? (
                    <ChevronUpIcon className="h-5 w-5 text-gray-500" />
                  ) : (
                    <ChevronDownIcon className="h-5 w-5 text-gray-500" />
                  )}
                </button>
                {expandedFAQ === i && (
                  <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
                    <p className="text-gray-700">{faq.answer}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-indigo-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">
            Ready to 10x Your Social Media?
          </h2>
          <p className="mt-4 text-xl text-gray-600">
            Join 5,000+ businesses already using Lily AI to dominate social media
          </p>
          <div className="mt-10">
            <Link
              to="/register"
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-8 py-4 rounded-lg text-lg font-semibold transition-colors inline-flex items-center"
            >
              Start Your Free Trial Today
              <ArrowRightIcon className="ml-2 h-5 w-5" />
            </Link>
          </div>
          <p className="mt-4 text-sm text-gray-500">
            14-day free trial • No setup fees • Cancel anytime
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="col-span-1 md:col-span-2">
              <h3 className="text-2xl font-bold text-white">Lily AI</h3>
              <p className="mt-4 text-gray-300 max-w-md">
                The most intelligent social media management platform. 
                Create, schedule, and optimize your content with AI.
              </p>
            </div>
            <div>
              <h4 className="text-lg font-semibold text-white">Product</h4>
              <ul className="mt-4 space-y-2">
                <li><a href="#features" className="text-gray-300 hover:text-white">Features</a></li>
                <li><a href="#pricing" className="text-gray-300 hover:text-white">Pricing</a></li>
                <li><Link to="/login" className="text-gray-300 hover:text-white">Sign In</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-lg font-semibold text-white">Company</h4>
              <ul className="mt-4 space-y-2">
                <li><a href="#" className="text-gray-300 hover:text-white">About</a></li>
                <li><a href="#" className="text-gray-300 hover:text-white">Privacy</a></li>
                <li><a href="#" className="text-gray-300 hover:text-white">Terms</a></li>
              </ul>
            </div>
          </div>
          <div className="mt-12 pt-8 border-t border-gray-700 text-center">
            <p className="text-gray-400">
              © 2025 Lily AI. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
      
      {/* Video Modal */}
      {showVideo && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-75" onClick={() => setShowVideo(false)}>
          <div className="bg-white p-4 rounded-lg max-w-4xl w-full mx-4">
            <div className="aspect-video bg-gray-200 flex items-center justify-center">
              {/* Replace with actual video embed */}
              <p className="text-gray-600">Demo video would play here</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default LandingPage