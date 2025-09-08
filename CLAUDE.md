- Only write production-ready code, no mock, fake, demo, or placeholder code
- Always write production ready code
- Never create mock data, designs, or code
- when making edits or additions, check any related API endpoints and ensure all are properly connected
- when finished make changes, test build, commit to remote git repo
- Unless explicity required, you (claude) will do everything you can to avoid manual intervention during the process of fixing, update, or editing this project

# Current System Status (September 2025) - Pressure Washing Focus

## Pressure Washing Specialization Complete ✅
- **COMPLETED**: Landing page transformed for pressure washing company targeting
- **Hero Section**: "The Only AI That Posts, Replies, and Books Jobs While You're On Site"
- **Features**: Combined autopilot with industry-specific benefits (DM→Booking, service knowledge)
- **Social Proof**: Updated testimonials from pressure washing companies with revenue metrics
- **FAQs**: Added pressure washing specific questions (soft wash, chemicals, rain delays)
- **SEO**: Updated metadata for pressure washing keywords and targeting

## OAuth Partner Integration Complete ✅
- **PHASE 4-8 COMPLETED**: Full partner OAuth integration system implemented
- **Connection Management**: OAuth-based Meta/X account connections with health monitoring
- **Rate Limiting**: Per-tenant rate limiting with Redis token bucket algorithm
- **Circuit Breakers**: Tenant-isolated fault tolerance for resilient publishing
- **Draft Verification**: Content scheduling with draft verification gates
- **Audit Logging**: Comprehensive connection management and publishing audit trails
- **Feature Flags**: `VITE_FEATURE_PARTNER_OAUTH` gating system for controlled rollout

## Current Production Deployment 🌐
- **Main API**: https://socialmedia-api-wxip.onrender.com (FastAPI backend)
- **Frontend**: https://lilymedia.ai (React app)
- **Database**: PostgreSQL with pgvector extension
- **Redis**: Configured for caching, rate limiting, and circuit breaker state
- **Status**: Production-ready with OAuth partner integrations

## AI Models & Services 🤖
- **Content Generation**: OpenAI GPT-4o and GPT-4o-mini (not GPT-5)
- **Image Generation**: xAI Grok-2 Vision model with streaming capabilities
- **Embeddings**: OpenAI text-embedding-3-large with 3072-dimensional vectors
- **Platform Integration**: Multi-platform optimization for X, Meta, Instagram

## Architecture Highlights 🏗️
- **Multi-tenant Isolation**: Organization-scoped access control and data separation
- **Resilient Publishing**: Connection-based publishing with retry and backoff
- **Performance Optimization**: Connection pooling, Redis caching, rate limiting
- **Security**: Encrypted token storage, secure OAuth flows, audit logging

## Recently Resolved Issues ✅
- **Authentication Flow**: Custom JWT system working correctly
- **Router Registry**: All API endpoints properly registered
- **Import Conflicts**: Resolved encryption module import issues
- **Test Coverage**: Comprehensive unit and integration test suites

## Current Capabilities - Pressure Washing Focus
- ✅ User registration and authentication (open SaaS)
- ✅ OAuth partner connections (Meta, X/Twitter)
- ✅ Industry-specific content creation (before/afters, seasonal promos)
- ✅ DM→Booking conversion flow
- ✅ Photo-to-estimate capability
- ✅ Service knowledge (soft wash vs pressure wash)
- ✅ Weather delay management
- ✅ Integration with Housecall Pro, Jobber, Calendly
- ✅ Revenue and job tracking (not just engagement metrics)
- ✅ Rate limiting and circuit breakers
- ✅ Connection health monitoring
- ✅ Draft verification system
- ✅ Audit logging and compliance
- research the internet to confirm the proper way to fix or produce what youre working on
- **NEW**: When working on pressure washing related features, consider industry-specific needs:
  - Seasonal business cycles (spring rush, winter prep)
  - Weather dependency and scheduling flexibility  
  - Service differentiation (pressure vs soft wash vs window cleaning)
  - Chemical safety and environmental concerns
  - Before/after visual content importance
  - Local market competition and pricing sensitivity
- Guardrail: production-ready only — no mock/fake/demo data in app code or migrations; mocks allowed in tests only; scan & confirm no banned patterns in the diff.

## Pressure Washing Industry Specialization 🚿

**Target Market**: Pressure washing and exterior cleaning companies
**Key Value Proposition**: Turn social media followers into booked jobs while you're on site

### Industry-Specific Features Implemented:
- **Service Knowledge**: AI understands soft wash vs pressure wash, chemical safety, plant protection
- **Photo Estimates**: Customers upload photos, get instant ballpark quotes for driveways, siding, roofs
- **Weather Management**: Handles rain delay questions, explains drying times, offers rescheduling
- **Seasonal Content**: Automatically promotes spring cleaning, gutter cleaning, holiday prep
- **Local Targeting**: Optimizes content for service areas and local market conditions
- **Tool Integration**: Direct integration with Housecall Pro, Jobber, Calendly for seamless workflow
- **Revenue Focus**: Tracks jobs booked and revenue generated, not just engagement metrics

### Marketing Positioning:
- **Pain Point**: Pressure washing owners are too busy on site to manage social media
- **Solution**: AI handles everything automatically while they work
- **Unique Differentiator**: Industry expertise + autopilot + job conversion
- **Target ROI**: 18+ jobs/month, $8.4K+ additional monthly revenue from social media