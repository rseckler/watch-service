-- Add image_url to watch_search_criteria
ALTER TABLE watch_search_criteria ADD COLUMN IF NOT EXISTS image_url TEXT;

-- Add image_url to watch_listings
ALTER TABLE watch_listings ADD COLUMN IF NOT EXISTS image_url TEXT;
