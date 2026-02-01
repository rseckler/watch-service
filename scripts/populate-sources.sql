-- Populate watch_sources with 17 pre-configured sources
-- Run this AFTER running 001_initial_schema.sql

-- ====================================================================
-- DEALERS (9 sources)
-- ====================================================================

INSERT INTO watch_sources (
  name, url, domain, type, scraper_type, active,
  search_url_template, listing_selector, title_selector, price_selector, link_selector,
  rate_limit_seconds, notes
) VALUES
('Cologne Watch', 'https://www.colognewatch.de', 'colognewatch.de', 'Dealer', 'Static', true,
 'https://www.colognewatch.de/search?q={manufacturer}+{model}', '.product-item', '.product-title',
 '.product-price', 'a.product-link', 2, 'Premium dealer in Cologne'),

('WatchVice', 'https://www.watchvice.de', 'watchvice.de', 'Dealer', 'Static', true,
 'https://www.watchvice.de/search?q={manufacturer}+{model}', '.product-card', 'h3.title',
 '.price', 'a.link', 2, NULL),

('Watch.de', 'https://www.watch.de', 'watch.de', 'Dealer', 'Static', true,
 'https://www.watch.de/suche?q={manufacturer}+{model}', '.watch-item', '.watch-name',
 '.watch-price', 'a', 2, NULL),

('Marks Uhren', 'https://www.marks-uhren.de', 'marks-uhren.de', 'Dealer', 'Static', true,
 'https://www.marks-uhren.de/search?q={manufacturer}+{model}', '.product', '.name',
 '.price-tag', 'a.product-link', 2, NULL),

('Rothfuss Watches', 'https://www.rothfuss-watches.de', 'rothfuss-watches.de', 'Dealer', 'Static', true,
 'https://www.rothfuss-watches.de/suche/{manufacturer}-{model}', '.item', '.title',
 '.preis', 'a', 2, NULL),

('Karmann Watches', 'https://www.karmannwatches.de', 'karmannwatches.de', 'Dealer', 'Static', true,
 'https://www.karmannwatches.de/search?q={manufacturer}+{model}', '.watch', 'h2',
 'span.price', 'a.watch-link', 2, NULL),

('Eupen Feine Uhren', 'https://www.eupenfeineuhren.de', 'eupenfeineuhren.de', 'Dealer', 'Static', true,
 'https://www.eupenfeineuhren.de/suche?q={manufacturer}+{model}', '.product-box', '.product-title',
 '.price', 'a', 2, NULL),

('G-Abriel', 'https://www.g-abriel.de', 'g-abriel.de', 'Dealer', 'Static', true,
 'https://www.g-abriel.de/search/{manufacturer}+{model}', '.article', 'h3.name',
 '.price-value', 'a', 2, NULL),

('Bachmann & Scher', 'https://www.bachmann-scher.de', 'bachmann-scher.de', 'Dealer', 'Static', true,
 'https://www.bachmann-scher.de/suche?q={manufacturer}+{model}', '.product', '.title',
 '.price-tag', 'a.link', 2, NULL);

-- ====================================================================
-- FORUMS (3 sources)
-- ====================================================================

INSERT INTO watch_sources (
  name, url, domain, type, scraper_type, active, requires_auth,
  auth_username_env, auth_password_env,
  search_url_template, listing_selector, title_selector, link_selector,
  rate_limit_seconds, notes
) VALUES
('Uhrforum.de', 'https://www.uhrforum.de', 'uhrforum.de', 'Forum', 'Forum', true, true,
 'UHRFORUM_USERNAME', 'UHRFORUM_PASSWORD',
 'https://www.uhrforum.de/search?q={manufacturer}+{model}', '.thread', '.thread-title',
 'a.thread-link', 3, 'Requires login: robin@seckler.de'),

('Watch Lounge Forum', 'https://forum.watchlounge.com', 'forum.watchlounge.com', 'Forum', 'Forum', true, true,
 'WATCHLOUNGE_USERNAME', 'WATCHLOUNGE_PASSWORD',
 'https://forum.watchlounge.com/search?q={manufacturer}+{model}', 'article.post', 'h3.title',
 'a.permalink', 3, NULL),

('Uhr-Forum.org', 'https://www.uhr-forum.org', 'uhr-forum.org', 'Forum', 'Forum', true, true,
 'UHR_FORUM_ORG_USERNAME', 'UHR_FORUM_ORG_PASSWORD',
 'https://www.uhr-forum.org/search?q={manufacturer}+{model}', '.post', '.post-title',
 'a.link', 3, NULL);

-- ====================================================================
-- MARKETPLACES (5 sources)
-- ====================================================================

INSERT INTO watch_sources (
  name, url, domain, type, scraper_type, active, requires_auth,
  auth_username_env, auth_password_env,
  search_url_template, listing_selector, title_selector, price_selector, link_selector,
  rate_limit_seconds, notes
) VALUES
('eBay.de', 'https://www.ebay.de', 'ebay.de', 'Marketplace', 'Marketplace', true, false,
 NULL, NULL,
 'https://www.ebay.de/sch/i.html?_nkw={manufacturer}+{model}', '.s-item', '.s-item__title',
 '.s-item__price', 'a.s-item__link', 5, 'Use eBay API if possible'),

('Kleinanzeigen.de', 'https://www.kleinanzeigen.de', 'kleinanzeigen.de', 'Marketplace', 'Marketplace', true, true,
 'KLEINANZEIGEN_USERNAME', 'KLEINANZEIGEN_PASSWORD',
 'https://www.kleinanzeigen.de/s-{manufacturer}-{model}/k0', '.ad-listitem', '.text-module-begin',
 '.aditem-main--middle--price', 'a.ellipsis', 5, 'Login: seckler@seckler.de'),

('Chrono24.de', 'https://www.chrono24.de', 'chrono24.de', 'Marketplace', 'Marketplace', true, false,
 NULL, NULL,
 'https://www.chrono24.de/search/index.htm?query={manufacturer}+{model}', '.article-item', '.article-title',
 '.article-price', 'a.article-link', 3, 'Premium marketplace'),

('Chronext.de', 'https://www.chronext.de', 'chronext.de', 'Marketplace', 'Marketplace', true, false,
 NULL, NULL,
 'https://www.chronext.de/search?query={manufacturer}+{model}', '.watch-card', '.watch-name',
 '.watch-price', 'a', 3, NULL),

('Uhrinstinkt.de', 'https://www.uhrinstinkt.de', 'uhrinstinkt.de', 'Marketplace', 'Marketplace', true, false,
 NULL, NULL,
 'https://www.uhrinstinkt.de/search?q={manufacturer}+{model}', '.listing', '.listing-title',
 '.listing-price', 'a.listing-link', 2, NULL);

-- ====================================================================
-- Verify
-- ====================================================================

SELECT
  type,
  COUNT(*) as count,
  COUNT(CASE WHEN active THEN 1 END) as active_count
FROM watch_sources
GROUP BY type
ORDER BY type;

-- Should show:
-- Dealer: 9 total, 9 active
-- Forum: 3 total, 3 active
-- Marketplace: 5 total, 5 active
-- TOTAL: 17 sources
