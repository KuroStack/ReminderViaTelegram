<?php

namespace App\Http\Controllers;

use App\Telegram\BotHandler;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;
use Telegram\Bot\Laravel\Facades\Telegram;

class TelegramWebhookController extends Controller
{
    public function __construct(private BotHandler $botHandler) {}

    public function handle(Request $request): JsonResponse
    {
        try {
            $update = Telegram::getWebhookUpdate();
            $this->botHandler->handle($update);
        } catch (\Throwable $e) {
            Log::error('Telegram webhook error: ' . $e->getMessage(), [
                'trace' => $e->getTraceAsString(),
            ]);
        }

        // Always return 200 — Telegram retries on non-200
        return response()->json(['ok' => true]);
    }
}
