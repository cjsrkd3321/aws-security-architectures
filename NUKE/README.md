# NUKE

[[AWS] How to delete unused resources with NUKE lambda using Python](https://medium.com/@7424069/aws-how-to-delete-unused-resources-with-nuke-lambda-using-python-7ed2f270480b)

## Architecture
![Architecture](./Architecture.png)

## Getting Started

1. Run docker
2. Start command `./layer.sh`
3. `terraform apply`
4. If you wanna spcific region, set REGIONS variable like below.(lambda_function.py)
```python
# REGIONS = get_regions()
REGIONS = ["us-east-1"]
```

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
