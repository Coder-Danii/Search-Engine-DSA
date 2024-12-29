export function cleanTag(tag) {
    // Remove quotes, brackets, and trim whitespace
    return tag.replace(/['"[\]]/g, '').trim();
  }
  