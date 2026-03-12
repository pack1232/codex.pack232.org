import { defineCollection, z } from 'astro:content';
import { docsSchema } from '@astrojs/starlight/schema';
import { glob } from 'astro/loaders';

/**
 * Content collection for the Ask Your SPL (youth) site.
 *
 * Imports youth roles, shared roles, shared resources, and training
 * from the shared content directory.
 */

const slug = z.string().regex(/^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$/);

const docs = defineCollection({
  loader: glob({
    pattern: [
      'roles/youth/**/*.md',
      'roles/shared/**/*.md',
      'roles/_shared/**/*.md',
      'roles/index.md',
      'training/**/*.md',
      'index.md',
      'CONTRIBUTING.md',
    ],
    base: '../../content',
  }),
  schema: docsSchema({
    extend: z.object({
      // Role fields
      role_id: slug.optional(),
      audience: z.enum(['adult', 'youth', 'both']).optional(),
      unit_type: z.enum(['pack', 'troop', 'crew', 'any']).optional(),
      works_with: z.array(z.string()).optional(),
      related_youth_roles: z.array(z.string()).optional(),
      related_adult_roles: z.array(z.string()).optional(),
      training_required: z.array(z.string()).optional(),

      // Training fields
      training_id: z.union([z.string(), z.number()]).optional(),
      training_code: z.union([z.string(), z.number()]).optional(),
      type: z.string().optional(),
      duration: z.union([z.string(), z.number()]).optional(),
      url: z.string().optional(),
      description: z.string().optional(),

      // Jekyll compatibility
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
