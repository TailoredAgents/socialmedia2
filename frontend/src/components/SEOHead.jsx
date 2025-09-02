import { Helmet } from 'react-helmet-async'

const SEOHead = ({ 
  title = "Lily AI: Autonomous AI Social Media Management for SMBs",
  description = "Save 90% time with AI autopilot for content, scheduling, and engagement across platforms. GPT-4o, Grok-2 Vision powered. 14-day free trial.",
  keywords = "AI social media management, autopilot social media, automated content creation, social media AI, SMB marketing automation",
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
    </Helmet>
  )
}

export default SEOHead