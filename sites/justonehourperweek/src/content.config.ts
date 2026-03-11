import { defineCollection, z } from 'astro:content';
import { docsSchema } from '@astrojs/starlight/schema';
import { glob } from 'astro/loaders';

// Shared optional fields from Jekyll that we preserve but don't require
const jekyllFields = {
  parent: z.string().optional(),
  nav_order: z.number().optional(),
  nav_exclude: z.boolean().optional(),
  layout: z.string().optional(),
  permalink: z.string().optional(),
};

const docs = defineCollection({
  loader: glob({ pattern: '**/*.md', base: '../../content' }),
  schema: docsSchema({
    extend: z.object({
      // Role fields
      role_id: z.string().optional(),
      audience: z.enum(['adult', 'youth', 'both']).optional(),

      // Task fields
      task_id: z.string().optional(),
      category: z.string().optional(),
      frequency: z.string().optional(),
      owner: z.string().optional(),
      roles: z.array(z.string()).optional(),
      tags: z.array(z.string()).optional(),
      timing_note: z.string().optional(),

      // Event fields
      event_id: z.string().optional(),
      months: z.union([z.array(z.number()), z.number()]).nullable().optional(),
      venue: z.string().optional(),

      // Training fields
      training_id: z.union([z.string(), z.number()]).optional(),
      training_code: z.union([z.string(), z.number()]).optional(),
      type: z.string().optional(),
      duration: z.union([z.string(), z.number()]).optional(),
      url: z.string().optional(),

      // Jekyll compatibility
      ...jekyllFields,
    }),
  }),
});

export const collections = { docs };
