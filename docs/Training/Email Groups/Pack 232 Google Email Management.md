---
title: "Pack 232 Email List Management Guide"
description: "We use Google Workspace to manage our email via the Google for Nonprofits program, which allows us access to all of the Google apps for free."
source_file: "Pack 232 Google Email Management.docx"
converted_date: "2026-03-06"
original_format: "docx"
author: "Unknown"
tags: ["email-groups", "camping", "training", "email"]
category: "Email Groups"
draft: false
---

By Josh McWilliam

We use Google Workspace to manage our email via the Google for Nonprofits program, which allows us access to all of the Google apps for free.
We use the Groups functionality to manage our email distribution lists / aliases. This allows us to maintain consistent email addresses for people to use while having flexibility to control who those emails are delivered to.

For a background of how we can to use Google Workspace and it’s many benefits, please see the following: Pack 232 Email Provider Analysis
# Email Types / Use Cases
There are three different primary ways in which we use Google Workspace to fulfill our email sending and receiving needs.
## Actual User Accounts for Key Roles
We need at least one actual user account to administer Google Workspace. The admin@pack232.com serves this role and is configured as the admin/owner of the account.

An actual user account is defined by the fact that it has its own login to our workspace and a separate email account that can be accessed via a normal mail client / app. While you can still configure that email address to forward to others, the primary way to use this is to “add an account” to your email app of choice and manage it separately.

Most people are likely to prefer having emails directed to them to simply be forwarded to their own personal email accounts. However, there are a number of reasons documented in the Pack 232 Email Provider Analysis that outline some of the use cases where an actual dedicated email user account would be advantageous.

The following users have been setup in this way:

### How to Access User Account
The username is the email address and the password must be obtained from either the Pack Admin or the prior person in that role.

As for the steps to access the account, some common ones are noted below, although if your email client / app or choice is not listed below, doing a Google search on how to do it will quickly yield the answer.
#### Via Web Interface
Go to https://mail.pack232.com (we have a custom domain setup for gmail. You can also use the default url)
Login using the email address and password for the account.

If you are already logged into another Gmail account you may also click on your user icon in the upper right part of the Gmail screen and click “Add another account”. This will allow you to easily switch back and forth between Gmail accounts by again clicking your user icon in the upper right of the screen.
#### Via an Email Client or App
If you have multiple email accounts, one advantage of many email apps is that it gives you a way to look at “All Inboxes”. This gives you the best of both worlds in that you can manage your multiple accounts as a single inbox while still having it reply and send as the specific account, or you can drill in and manage each account / inbox separately, your choice.

Mobile Phones
Add or remove an account on Android
Use your Google Account on your iPhone or iPad
How to Set Up Gmail with a Desktop Mail Client

## Public / Inbound Email Aliases
These are email addresses that the public might use. They typically go to either a single person or a small group of people. They are primarily meant to receive email, not send it. Examples of these include:

These groups should use the following access permissions, with the key change over the default being that “External” people can post to the group.

## Internal / Outbound Email Lists
These email addresses are meant for internal communication for the most part. They are meant to allow easy sending to a group of people (ie. Entire Pack, Den, etc.) while also making sure that only people in the group can send to the group.

### Group Permissions
#### All Member Groups

For the types of groups where all members of that group should be able to send to the group, the following permissions should be used.

Access Settings = Restricted. The right combination of permissions to allow group members to send to the list but not external people who are not on the list. This also gives permission to the group owner/manager to manage who is on the list.
Who can join the group = Only invited users. We only want people who have been added by the group owner/manager included in the list.
Allow members outside your organization = YES. Makes it so the group owner/manager can add people’s personal addresses to the list.

#### Restricted Email Announcement Only Groups

For the large email-blast only types of groups where we want to restrict who can send to the group (ie. announce@pack232.com) we should use the same settings as above, but the “Announcement Only” access settings should be used:

# Administering Users (Actual Email Accounts)
This is not something that will need to be done very often, but the Pack Admin (admin@pack232.com) may find the need to do some of the following:

Create New User (unlikely)
Reset a User Password (more likely)

To administer User accounts, go to https://admin.google.com, login as the admin@pack232.com user and then select “Users” to administer them. Another way to get to this if you are already logged into Gmail for that account, clicking on the Gear icon in the upper right and selecting “Manage this Domain” will also get you into the Google Admin interface.
# Administering Groups (Email Lists)
Groups may be administered in one of two ways:

## Google Workspace Admin

## Google Groups

| User | Reason for User Account |
| --- | --- |
| admin@pack232.com | Core required account, but also valuable to collect past IT related email history. Note that this is also configured at the catchall for any email received to the domain that is not associated with a valid user or group. |
| cubmaster@pack232.com | Leader of the organization should be able to send and receive emails as the Cubmaster and a new Cubmaster should be able to benefit from the history of communications when they take over. For redundancy purposes (and convenience), this account should also be given Super Admin privileges. |
| treasurer@pack232.com | Important account with lots of history and tied to several important logins to other 3rd party systems (ie. Quickbooks, Paypal, Banks, etc.). It is also useful to have all files uploaded by treasurer (ie. receipts) not owned by someone’s personal account. |

| Group | Recipient(s) |
| --- | --- |
| cubmaster@pack232.com | Cubmaster & Assistant Cubmaster |
| chair@pack232.com | Committee Chair |
| col@pack232.com | Charter Org. Rep |
| money@pack232.com | Treasurer |
| membership@pack232.com | Membership Chair / Coordinator |
| fundraising@pack232.com | Fundraising Chair / Popcorn Kernel |
| advancement@pack232.com | Advancement Chair |
| webmaster@pack232.com | Pack Webmaster / IT Chair |

| Group | Recipient(s) | Sending Permission |
| --- | --- | --- |
| announce@pack232.com | All active families and leaders. | Cubmaster, Treasurer, Chair, Fundraising |
| den#@pack232.com | There is one for each den and the # is to be replaced by the den number (ie. den6@pack232.com) and the list should include all members of that den | All group members |
