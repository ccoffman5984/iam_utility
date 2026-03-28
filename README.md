# iam_utility

A small AWS IAM utility for disabling IAM Access Keys older than 30 days across one or more AWS accounts using an AssumeRole workflow.

## Repository contents

- `disable_access_keys.py`
  - Python script that assumes an AWS IAM role in the target account and disables IAM access keys older than 30 days.
  - Uses `boto3` via `sts.assume_role` and `iam.list_users` / `iam.list_access_keys` / `iam.update_access_key`.

- `process_listing.sh`
  - Bash wrapper to process a list of AWS account IDs from a file and execute `disable_access_keys.py` for each account.

- `inputs.txt`
  - Example account list file, one AWS account ID per line (not required name; plain 12-digit account IDs).

## Prerequisites

- Python 3.8+
- `boto3` installed (`pip install boto3`).
- AWS CLI credentials configured for an account that can assume the target role in managed accounts.
- In target accounts, an IAM role named `DisableAccessKeys` must exist with a trust relationship allowing the source role:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"AWS": "arn:aws:iam::<control-account-id>:role/<role-name>"},
      "Action": "sts:AssumeRole"
    }
  ]
}
```

### Role permissions in each target account

The `DisableAccessKeys` role needs permissions such as:

- `iam:ListUsers`
- `iam:ListAccessKeys`
- `iam:UpdateAccessKey`

## Usage

1. Populate `inputs.txt` or another file with one account ID per line:

```text
123456789012
234567890123
345678901234
```

2. Run the script:

```bash
./process_listing.sh inputs.txt
```

3. The script prints per-account and per-user key status and disables keys older than 30 days.

## `disable_access_keys.py` behavior

- Reads target account from command-line argument:
  - `python disable_access_keys.py <account_id>`
- Calls `sts.assume_role` with role ARN: `arn:aws:iam::<account_id>:role/DisableAccessKeys`.
- Uses temporary credentials to initialize an IAM client.
- Lists all IAM users in the account.
- For each user, lists access keys and checks age in days.
- Disables (sets status `Inactive`) any key whose age is strictly greater than 30 days.

## Security notes

- This tool is destructive (it disables keys); use carefully in non-production first.
- Audit and document excepted keys before running in production.
- Manage least privilege for both the calling principal and the `DisableAccessKeys` role.

## Troubleshooting

- `AccessDenied` or `UnauthorizedOperation` means IAM role trust/policies are missing.
- If `list_users` returns empty, ensure the account has users and you are in the right region (IAM is global).
- If 404 on `disable_access_keys.py`, verify script path and Python version.

## Improvements (optional)

- Add CLI flags for key age threshold, role name, and dry-run mode.
- Add pagination support for `list_users` and `list_access_keys` for accounts with >1000 users/keys.
- Add logging to file and structured output (JSON).
 