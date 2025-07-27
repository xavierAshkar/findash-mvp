from core.models import Tag

def auto_tag_transaction(user, transaction):
    """
    Auto-tags a transaction based on its category_main.
    - Creates a Tag if it doesn't already exist for the user.
    - Assigns the Tag to the transaction.
    """
    if not transaction.category_main:
        return  # Nothing to tag

    # Normalize name (lowercase, strip spaces)
    tag_name = transaction.category_main.lower().strip()

    # Find or create the tag for this user
    tag, _ = Tag.objects.get_or_create(user=user, name=tag_name)

    # Assign the tag if not already set
    if transaction.tag_id != tag.id:
        transaction.tag = tag
        transaction.save()