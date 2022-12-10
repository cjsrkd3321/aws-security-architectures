# NUKE

[How to delete unused resources with lambda NUKE in python (Not written yet)]()

## Getting Started
1. Run docker
2. Start command `./layer.sh`
3. `terraform apply`

## Cautions

1. If you wanna test this NUKE, be careful! Because test codes can spend a lot of money probably.

2. You can add other resources. And contribute to this NUKE. **YOU NEED TO ADD WITH TEST CODE USING TERRAFORM.**

3. It has default filters like below.

- I recommend you must test this NUKE first using "have_no_nuke_project_tag".
- And, Start "have_tags" filter for deleting unused resources.
- Finally, You can add custom filter!

```python
# pool.submit(lister, r, sessions[region][svc], have_no_nuke_project_tag) # FOR TEST
# pool.submit(lister, r, sessions[region][svc], is_create_date_less_than_now)
# pool.submit(lister, r, sessions[region][svc], have_tags)  # NO TAGS
# pool.submit(lister, r, sessions[region][svc]) # ALL RESOURCES
```

## References

- [aws-nuke](https://github.com/rebuy-de/aws-nuke)

## Special Thanks

- Thank you so much to "aws-nuke". Without you, this project could not have been successful.
