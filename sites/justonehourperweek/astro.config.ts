import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  site: 'https://justonehourperweek.com',
  integrations: [
    starlight({
      title: 'Just One Hour Per Week',
      description: 'A volunteer knowledge base for Cub Scout pack leaders',
      social: [
        { icon: 'github', label: 'GitHub', href: 'https://github.com/pack232/codex.pack232.org' },
      ],
      sidebar: [
        { label: 'Home', link: '/' },
        {
          label: 'Organization',
          items: [
            { label: 'Org Chart', link: '/org-chart/' },
          ],
        },
        {
          label: 'Roles',
          items: [
            { label: 'All Roles', link: '/roles/' },
            {
              label: 'Adult Roles',
              autogenerate: { directory: 'roles/adult' },
              collapsed: true,
            },
            {
              label: 'Shared Roles',
              autogenerate: { directory: 'roles/shared' },
              collapsed: true,
            },
            {
              label: 'Youth Roles',
              autogenerate: { directory: 'roles/youth' },
              collapsed: true,
            },
          ],
        },
        {
          label: 'Tasks',
          autogenerate: { directory: 'tasks' },
          collapsed: true,
        },
        {
          label: 'Events',
          autogenerate: { directory: 'events' },
          collapsed: true,
        },
        {
          label: 'Training',
          autogenerate: { directory: 'training' },
          collapsed: true,
        },
        {
          label: 'Shared Resources',
          items: [
            { label: 'Training Requirements', link: '/roles/_shared/training-requirements/' },
            { label: 'BSA Policies', link: '/roles/_shared/bsa-policies/' },
            { label: 'Annual Calendar', link: '/roles/_shared/calendar/' },
          ],
        },
      ],
      customCss: ['./src/styles/custom.css'],
      components: {
        Head: './src/components/Head.astro',
      },
    }),
  ],
});
