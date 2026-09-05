# Post-purchase email: selling refills

The refill plan is not sold in the buy box. It cannot be bought there yet, and
putting an option on a page that takes an order it will never fulfil is the trap
we avoided twice already. So refills are sold after the gun, by email, where a
one-time order works today and the plan can be added the day the subscription
app is live.

Four emails, branching on what the customer bought. Nothing here is automatic:
the customer clicks, or nothing happens.

## Timing

| | Gun only (1 pod) | Gun + 3 pods |
|---|---|---|
| 1. Did it work? | Day 2 | Day 2 |
| 2. Running low | Day 18 | Day 45 |
| 3. Stop thinking about it | Day 25 | Day 55 |
| 4. Last nudge | Day 40 | Day 70 |

> **The pod-life numbers do not agree with each other yet.** The page says one
> pod treats a living room about 25 times, and that households go through three
> every two months. Those two only reconcile at roughly nine treatments a week.
> Row 16 of the spec gate settles it, and these send dates move when it does.

---

## 1. Day 2 — Did it work?

Sells nothing. It exists to get the tests run while the 30-day window is open,
which is what turns a refund into a repeat customer.

**Formula: ACC · Psychology: Reciprocity, Cognitive Ease · NLP: Presupposition**

**Subject:** `Run the tissue test today` (25)
**Preview:** `Two minutes, and you will know exactly what you bought.` (55)

> Your VelaHush landed a couple of days ago.
>
> Before the week gets away from you, run the three tests. They take about two
> minutes between them and they tell you more than any review would.
>
> **The stopwatch.** Time one pass over the sofa, then press a dry palm into the
> cushion. It should come back dry.
>
> **The tissue.** Hold one a foot from the nozzle for two seconds. Faintly cool,
> still readable. If it comes back wet, something is wrong and we want to know.
>
> **The trigger count.** Count the passes for one room. That number is what your
> running cost is built on.
>
> If any of them disappoint you, reply to this email. You have 30 days and you
> keep the pods either way.
>
> `[ How to use it on car seats ]`
>
> P.S. Nose-blindness works fast. Ask someone who does not live with you before
> you decide it did nothing.

---

## 2. Day 18 / 45 — Running low

**Formula: PAS · Psychology: Cost of Inaction, Specificity Bias · NLP: Presupposition, Double Bind**

**Subject:** `You are about a week from empty` (31)
**Preview:** `Three pods, $21, in whichever scent you have been using.` (56)

> Going by the day you bought, you are around a week from the end of your
> {{ pod_count }}.
>
> Nothing happens automatically here. No card on file, no shipment you have to
> stop. If you want more, you order them.
>
> Three pods are $21. That is roughly two months for most households, and it is
> the same {{ scent }} you have been using unless you change it at checkout.
>
> `[ Order three pods, $21 ]`
>
> If the timing is off, ignore this. We will send one more and then leave you
> alone.
>
> P.S. The gun is not locked to our pods. Any water-based enzyme cleaner works
> and it will not void your warranty. We would rather you knew that from us.

---

## 3. Day 25 / 55 — Stop thinking about it

The plan offer. **Do not send until the subscription app is live and the plan is
attached to the refill product.** Until then, send email 4 instead.

**Formula: BAB · Psychology: Loss Aversion, Anchoring, Risk Reversal · NLP: Pacing & Leading, Double Bind**

**Subject:** `The part everyone forgets` (25)
**Preview:** `Pods that turn up on their own, 15% cheaper than ordering them.` (63)

> Here is how this usually goes. The gun works, the house stops smelling, and
> four months later you notice the smell is back and realise you ran out weeks
> ago.
>
> That is the whole failure mode. Not the product. The remembering.
>
> Three pods every two months, sent before you run out, at $17.85 instead of
> $21. Change the scent, push a delivery back a month, or cancel outright. Every
> link is in every email.
>
> No phone call, no retention script, no "are you sure" three times.
>
> `[ Set up the refill plan, $17.85 ]`
>
> Prefer to keep ordering them yourself? That option is not going anywhere.
>
> P.S. You can cancel from the first email, before the second delivery ever
> ships. That is not a trick, it is just how we set it up.

---

## 4. Day 40 / 70 — Last nudge

**Formula: PAS short · Psychology: Loss Aversion · NLP: Embedded Command**

**Subject:** `Last one about pods` (19)
**Preview:** `Then we stop. Your gun works with any water-based cleaner anyway.` (65)

> This is the last email about refills.
>
> If you have run out and gone back to the candles, three pods are $21 and they
> ship the same working day.
>
> If you are using your own solution, good. It works, it does not void the
> warranty, and we would rather you use the gun than shelve it.
>
> `[ Order three pods, $21 ]`
>
> P.S. Water-based only. Nothing oily, thick, or solvent-based. That is the one
> repair the warranty does not cover.

---

## Deliverability notes

Every subject is under 50 characters and every preview under 90, per the email
preset. None uses the words free, buy now, urgent, or all caps, and each email
carries one primary link.

Email 1 links to content rather than a product, which is deliberate: a first
post-purchase email that sells reads as a shop that already wants more money.

## What to change when things land

- **Spec row 16** decides the real pod life, and every send date above.
- **Subscription app live** unlocks email 3. Until then it stays off.
- **Real reviews** would give email 1 a natural ask. Not before, per the review
  policy on the page.
