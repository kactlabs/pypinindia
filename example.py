#added a method get_postoffice_summary to returns a summarized count of post offices by their type and delivery status for a given pincode.


from pinin import get_postoffice_summary

def main():
    print("\n2. Post Office Summary")
    print("-" * 30)
    summary = get_postoffice_summary("110001")
    print(summary)


if __name__ == "__main__":
    main()


# from pinin.exceptions import SummaryError

# def test_summary_error():
#     print("\n3. Summary Error Test")
#     print("-" * 30)
#     try:
#         # Use an invalid pincode that causes summary error (simulate it manually if needed)
#         raise SummaryError("123456")
#     except SummaryError as e:
#         print(f"Caught SummaryError: {e}")
# if __name__ == "__main__":
#     # main()
#     test_summary_error()
