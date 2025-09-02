import { Helmet } from 'react-helmet-async'

const SEOHead = ({ 
  title = "Lily AI - AI Social Media Autopilot for SMBs",
  description = "Autonomous AI for social media: Research trends, create content, schedule posts, handle responses. Save 90% time for SMBs.",
  keywords = "AI social media management, autopilot SaaS, SMB tools",
  url = "https://socialmedia-frontend-pycc.onrender.com",
  image = "https://socialmedia-frontend-pycc.onrender.com/og-image.jpg"
}) => {
  return (
    <Helmet>
      {/* Primary Meta Tags */}
      <title>{title}</title>
      <meta name="title" content={title} />
      <meta name="description" content={description} />
      <meta name="keywords" content={keywords} />
      <meta name="robots" content="index, follow" />
      <meta name="language" content="English" />
      <meta name="author" content="Lily AI" />

      {/* Open Graph / Facebook */}
      <meta property="og:type" content="website" />
      <meta property="og:url" content={url} />
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:image" content={image} />
      <meta property="og:site_name" content="Lily AI" />

      {/* Twitter */}
      <meta property="twitter:card" content="summary_large_image" />
      <meta property="twitter:url" content={url} />
      <meta property="twitter:title" content={title} />
      <meta property="twitter:description" content={description} />
      <meta property="twitter:image" content={image} />

      {/* Additional Meta Tags */}
      <meta name="theme-color" content="#2563eb" />
      <meta name="msapplication-TileColor" content="#2563eb" />
      
      {/* Preconnect to optimize loading */}
      <link rel="preconnect" href="https://fonts.googleapis.com" />
      <link rel="preconnect" href="https://images.unsplash.com" />
      
      {/* Canonical URL */}
      <link rel="canonical" href="https://socialmedia-frontend-pycc.onrender.com/" />
      
      {/* Product Schema */}
      <script type="application/ld+json">
        {JSON.stringify({
          "@context": "https://schema.org",
          "@type": "Product",
          "name": "Lily AI Social Media Management Platform",
          "description": description,
          "url": url,
          "brand": {
            "@type": "Brand",
            "name": "Lily AI"
          },
          "category": "Social Media Management Software",
          "offers": [
            {
              "@type": "Offer",
              "name": "Starter Plan",
              "price": "59",
              "priceCurrency": "USD",
              "billingDuration": "P1M",
              "availability": "https://schema.org/InStock",
              "validFrom": "2024-01-01",
              "priceValidUntil": "2025-12-31",
              "seller": {
                "@type": "Organization",
                "name": "Lily AI"
              }
            },
            {
              "@type": "Offer",
              "name": "Pro Plan",
              "price": "149",
              "priceCurrency": "USD",
              "billingDuration": "P1M",
              "availability": "https://schema.org/InStock",
              "validFrom": "2024-01-01",
              "priceValidUntil": "2025-12-31",
              "seller": {
                "@type": "Organization",
                "name": "Lily AI"
              }
            },
            {
              "@type": "Offer",
              "name": "Enterprise Plan",
              "price": "499",
              "priceCurrency": "USD",
              "billingDuration": "P1M",
              "availability": "https://schema.org/InStock",
              "validFrom": "2024-01-01",
              "priceValidUntil": "2025-12-31",
              "seller": {
                "@type": "Organization",
                "name": "Lily AI"
              }
            }
          ],
          "applicationCategory": "BusinessApplication",
          "operatingSystem": "Web Browser",
          "softwareVersion": "1.0",
          "releaseDate": "2024-01-01",
          "featureList": [
            "Autonomous AI content creation",
            "Multi-platform social media management",
            "Advanced analytics and insights",
            "Team collaboration tools",
            "Enterprise-grade security"
          ],
          "screenshot": "https://socialmedia-frontend-pycc.onrender.com/screenshot.jpg",
          "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "4.8",
            "reviewCount": "150",
            "bestRating": "5",
            "worstRating": "1"
          }
        })}
      </script>

      {/* Organization Schema */}
      <script type="application/ld+json">
        {JSON.stringify({
          "@context": "https://schema.org",
          "@type": "Organization",
          "name": "Lily AI",
          "url": url,
          "logo": {
            "@type": "ImageObject",
            "url": "https://socialmedia-frontend-pycc.onrender.com/logo.png",
            "width": "200",
            "height": "200"
          },
          "contactPoint": {
            "@type": "ContactPoint",
            "telephone": "+1-800-LILY-AI",
            "contactType": "Customer Service",
            "areaServed": "Worldwide",
            "availableLanguage": ["English"]
          },
          "sameAs": [
            "https://twitter.com/lilyai",
            "https://linkedin.com/company/lily-ai"
          ],
          "address": {
            "@type": "PostalAddress",
            "streetAddress": "123 AI Street",
            "addressLocality": "San Francisco",
            "addressRegion": "CA",
            "postalCode": "94105",
            "addressCountry": "US"
          },
          "foundingDate": "2024",
          "numberOfEmployees": "50-100"
        })}
      </script>

      {/* FAQ Structured Data */}
      <script type="application/ld+json">
        {JSON.stringify({
          "@context": "https://schema.org",
          "@type": "FAQPage",
          "mainEntity": [
            {
              "@type": "Question",
              "name": "What makes Lily AI different from other social media tools?",
              "acceptedAnswer": {
                "@type": "Answer",
                "text": "Lily AI is the only platform offering full autonomous autopilot mode—no human oversight needed. Our AI researches trends, creates content, schedules posts, and handles engagement completely on its own. Competitors require constant manual input."
              }
            },
            {
              "@type": "Question",
              "name": "Which social media platforms are supported?",
              "acceptedAnswer": {
                "@type": "Answer",
                "text": "We support all major platforms: X (Twitter), Meta (Facebook & Instagram), LinkedIn, TikTok, YouTube, and Threads. More platforms are added regularly based on user demand."
              }
            },
            {
              "@type": "Question",
              "name": "How secure is my data and social media accounts?",
              "acceptedAnswer": {
                "@type": "Answer",
                "text": "Enterprise-grade security with JWT authentication, end-to-end encryption, audit logs, and full GDPR/CCPA compliance. Your data is more secure with us than managing accounts manually."
              }
            },
            {
              "@type": "Question",
              "name": "How does the 14-day free trial work?",
              "acceptedAnswer": {
                "@type": "Answer",
                "text": "Full access to all features for 14 days. If you love it (which you will), seamlessly upgrade to continue. Cancel anytime during trial with zero charges."
              }
            }
          ]
        })}
      </script>
    </Helmet>
  )
}

export default SEOHead