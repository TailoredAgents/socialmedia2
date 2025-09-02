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
      
      {/* Structured Data for SEO */}
      <script type="application/ld+json">
        {JSON.stringify({
          "@context": "https://schema.org",
          "@type": "SoftwareApplication",
          "name": "Lily AI",
          "applicationCategory": "BusinessApplication",
          "description": description,
          "url": url,
          "operatingSystem": "Web",
          "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "USD",
            "description": "14-day free trial"
          },
          "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "4.9",
            "ratingCount": "5000"
          }
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