import { defineCollection, z } from 'astro:content';
import { docsSchema } from '@astrojs/starlight/schema';
import { glob } from 'astro/loaders';

/**
 * Content collection for the Just One Hour Per Week Starlight site.
 *
 * All content lives in ../../content/ and follows the BSA content pack schema.
 * Fields are optional at the Astro level because the collection includes
 * index/category pages that don't carry content-type-specific IDs.
 *
 * Strict validation happens in CI via scripts/validate-content.ts.
 */

// Slug pattern: lowercase, hyphens, digits
const slug = z.string().regex(/^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$/);

const docs = defineCollection({
  loader: glob({ pattern: '**/*.md', base: '../../content' }),
  schema: docsSchema({
    extend: z.object({
      // ── Role fields ──
      role_id: slug.optional(),
      audience: z.enum(['adult', 'youth', 'both']).optional(),
      unit_type: z.enum(['pack', 'troop', 'crew', 'any']).optional(),
      works_with: z.array(z.string()).optional(),
      related_youth_roles: z.array(z.string()).optional(),
      related_adult_roles: z.array(z.string()).optional(),
      training_required: z.array(z.string()).optional(),

      // ── Task fields ──
      task_id: slug.optional(),
      category: z.string().optional(),
      frequency: z.string().optional(),
      owner: z.string().optional(),
      roles: z.array(z.string()).optional(),
      tags: z.array(z.string()).optional(),
      timing_note: z.string().optional(),
      event: z.string().optional(),

      // ── Event fields ──
      event_id: slug.optional(),
      months: z.union([z.array(z.number()), z.number()]).nullable().optional(),
      venue: z.string().optional(),

      // ── Training fields ──
      training_id: z.union([z.string(), z.number()]).optional(),
      training_code: z.union([z.string(), z.number()]).optional(),
      type: z.string().optional(),
      duration: z.union([z.string(), z.number()]).optional(),
      url: z.string().optional(),

      // ── Jekyll compatibility (preserved, not required) ──
      parent: z.string().optional(),
      nav_order: z.number().optional(),
      nav_exclude: z.boolean().optional(),
      layout: z.string().optional(),
      permalink: z.string().optional(),
      has_children: z.boolean().optional(),
    }),
  }),
});

export const collections = { docs };
