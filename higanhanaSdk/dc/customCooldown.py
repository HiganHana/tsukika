from discord.ext import commands

class CustomCooldown:
    def __init__(self, rate, per, alter_rate, alter_per, bucket, *, elements, reverse: bool = False):
        self.elements = elements
        # Default mapping is the default cooldown
        self.default_mapping = commands.CooldownMapping.from_cooldown(rate, per, bucket)
        # Alter mapping is the alternative cooldown
        self.alter_mapping = commands.CooldownMapping.from_cooldown(alter_rate, alter_per, bucket)
        # Copy of the original BucketType
        self._bucket_type = bucket
        
        #
        self.reverse = reverse

    def __call__(self, ctx):
        key = self.alter_mapping._bucket_key(ctx.message)

        if self._bucket_type is commands.BucketType.member: # `BucketType.member` returns a tuple
            key = key[1] # The second (last) value is the member ID, the first one is the guild ID

        if (not self.reverse and key in self.elements) or (self.reverse and key not in self.elements):
            # If the key is in the elements, the bucket will be taken from the alternative cooldown
            bucket = self.alter_mapping.get_bucket(ctx.message)
        else:
            # If not, from the default cooldown
            bucket = self.default_mapping.get_bucket(ctx.message)

        # Getting the ratelimit left (can be None)
        retry_after = bucket.update_rate_limit()

        if retry_after: # If the command is on cooldown, raising the error
            raise commands.CommandOnCooldown(bucket, retry_after)
        return True