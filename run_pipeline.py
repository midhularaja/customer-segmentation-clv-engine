from src.rfm_segmentation import main as run_rfm
from src.market_basket import main as run_market_basket
from src.validate_champions import validate_champions  

def main():
    print("Running RFM Segmentation...")
    run_rfm()

    print("Running Market Basket Analysis...")
    run_market_basket()

    print("Validating Champions segment...")
    validate_champions()  

    print("Pipeline completed successfully.")

if __name__ == "__main__":
    main()
